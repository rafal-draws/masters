pub mod user_http {
    use std::env;

    use askama::Template;
    use axum::{
        extract::{Multipart, Path},
        http::{
            header::{LOCATION, SET_COOKIE},
            HeaderValue, Response, StatusCode,
        },
        response::{Html, IntoResponse, Redirect},
        Form,
    };
    use axum_extra::extract::CookieJar;
    use chrono::NaiveDateTime;
    use serde::Deserialize;
    use tokio::{fs::File, io::AsyncWriteExt};

    use crate::db::db_conn::{
        delete_upload, get_all_uploads, get_default_upload, get_user_by_uuid, insert_upload_to_db,
        Upload, User,
    };

    #[derive(Template)]
    #[template(path = "upload_successful.html")]
    pub struct UploadTemplate {
        title: String,
        upload_uuid: String,
        bytes: usize,
    }

    pub async fn upload_track(
        jar: CookieJar,
        mut multipart: Multipart,
    ) -> Result<HtmlTemplate<UploadTemplate>, StatusCode> {
        if let Some(uuid) = jar.get("uuid") {
            let user = get_user_by_uuid(&uuid.value().to_string()).await.unwrap();

            let mut template: UploadTemplate = UploadTemplate {
                upload_uuid: "".to_string(),
                title: "".to_string(),
                bytes: 0,
            };

            while let Some(field) = multipart.next_field().await.unwrap() {
                let name = field.name().unwrap().to_string();
                let file_name = field.file_name().unwrap().to_string();

                let suffix = file_name
                    .split(".")
                    .into_iter()
                    .last()
                    .expect("Should contain suffix");

                match suffix {
                    "mp3" | "wav" => println!("file is .wav or mp3"),
                    _ => return Err(StatusCode::FORBIDDEN),
                }

                let data = field.bytes().await.unwrap();

                let mut file = File::create(format!(
                    "{}/{}-{}",
                    env::var("UPLOADS_DIR").unwrap(),
                    uuid.value(),
                    file_name
                ))
                .await
                .unwrap();
                let _ = file.write_all(&data);

                let upload = insert_upload_to_db(&user.uuid, &file_name).await;

                tracing::debug!(
                    "Length of `{name}` (`{}`: `{}`) is {} bytes. \n\n User session: {}, {}",
                    upload.file_name,
                    upload.upload_uuid,
                    data.len(),
                    user.username,
                    upload.user_uuid
                );

                template.bytes = data.len();
                template.title = upload.file_name;
                template.upload_uuid = upload.upload_uuid;
            }

            Ok(HtmlTemplate(template))
        } else {
            Err(StatusCode::CONFLICT)
        }
    }

    #[derive(Template)]
    #[template(path = "delete_status.html")]
    pub struct DeleteStatus {
        pub upload_uuid: String,
        pub user_uuid: String,
        pub status: bool,
    }

    pub async fn delete_upload_http(
        Path(upload_uuid): Path<String>,
        jar: CookieJar,
    ) -> impl IntoResponse {
        if let Some(uuid) = jar.get("uuid") {
            let result = delete_upload(upload_uuid.clone(), uuid.value().to_string()).await;
            HtmlTemplate(result).into_response()
        } else {
            (
                StatusCode::BAD_REQUEST,
                HtmlTemplate(DeleteStatus {
                    upload_uuid: "".to_string(),
                    user_uuid: "".to_string(),
                    status: false,
                }),
            )
                .into_response()
        }
    }

    #[derive(Template)]
    #[template(path = "user_metadata.html")]
    pub struct UserMetadataTemplate {
        pub username: String,
        pub uuid: String,
        pub created_at: NaiveDateTime,
        pub uploads: Vec<Upload>,
    }

    pub async fn get_user_data(
        jar: CookieJar,
    ) -> Result<HtmlTemplate<UserMetadataTemplate>, StatusCode> {
        if let Some(uuid) = jar.get("uuid") {
            let user = get_user_by_uuid(&uuid.value().to_string())
                .await
                .expect("Should have a session");
            let uploads = get_all_uploads(&uuid.value().to_string())
                .await
                .unwrap_or(get_default_upload());
            let template = UserMetadataTemplate {
                username: user.username,
                uuid: user.uuid,
                created_at: user.created_at,
                uploads: uploads,
            };
            Ok(HtmlTemplate(template))
        } else {
            return Err(StatusCode::NOT_FOUND);
        }
    }

    #[derive(Deserialize, Debug)]
    pub struct UserRegisterReq {
        pub username: String,
    }

    pub async fn register_user(Form(data): Form<UserRegisterReq>) -> impl IntoResponse {
        println!("extracted: {:?}", &data);

        let user = User::new(data.username).await;
        // create_user(); GENERATE UUID + PERSIST IN DATABASE (id, uuid, username, creation_date)
        let cookie = format!("uuid={}; Path:/; HttpOnly; SameSite=Strict", &user.uuid);

        Response::builder()
            .status(StatusCode::FOUND)
            .header(SET_COOKIE, HeaderValue::from_str(&cookie).unwrap())
            .header(LOCATION, "/register")
            .body(axum::body::Body::empty())
            .unwrap()
    }

    pub async fn user_registered(jar: CookieJar) -> impl IntoResponse {
        if let Some(uuid) = jar.get("uuid") {
            Html(format!(
                "uuid: {}, <a href='/profile'>Go to profile</a>",
                uuid.value()
            ))
        } else {
            Html("No UUID found in cookies.".to_string())
        }
    }

    pub async fn user_form(jar: CookieJar) -> Result<HtmlTemplate<UserFormTemplate>, Redirect> {
        if let Some(_uuid) = jar.get("uuid") {
            // TODO check for cookie forgery
            Err(Redirect::temporary("/profile"))
        } else {
            let template = UserFormTemplate {};
            Ok(HtmlTemplate(template))
        }
        // let template = UserFormTemplate{};
        // HtmlTemplate(template)
    }

    #[derive(Template)]
    #[template(path = "form.html")]
    pub struct UserFormTemplate {}

    pub struct HtmlTemplate<T>(T);

    impl<T> IntoResponse for HtmlTemplate<T>
    where
        T: Template,
    {
        fn into_response(self) -> axum::response::Response {
            match self.0.render() {
                Ok(html) => Html(html).into_response(),
                Err(err) => (
                    StatusCode::INTERNAL_SERVER_ERROR,
                    format!("Failed to render template. Error {err}"),
                )
                    .into_response(),
            }
        }
    }
}
