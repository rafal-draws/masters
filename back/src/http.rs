pub mod user_http {
    use std::env;

    use askama::Template;
    use axum::{extract::Multipart, http::{header::{LOCATION, SET_COOKIE}, HeaderValue, Response, StatusCode}, response::{Html, IntoResponse, Redirect}, Form};
    use axum_extra::extract::CookieJar;
    use chrono::NaiveDateTime;
    use serde::Deserialize;
    use tokio::{fs::File, io::AsyncWriteExt};

    use crate::db::db_conn::{get_user_by_uuid, User};

    pub async fn upload_track(
        mut multipart: Multipart
    )  {

    while let Some(field) = multipart.next_field().await.unwrap() {
        let name = field.name().unwrap().to_string();
        let file_name = field.file_name().unwrap().to_string();
        let content_type = field.content_type().unwrap().to_string();
        let data = field.bytes().await.unwrap();

        let mut file = File::create(format!("{}/{}",
                                                        env::var("UPLOADS_DIR").unwrap(),
                                                        file_name))
                                                        .await.unwrap();
        let _ = file.write_all(&data);
        
        // If everything worked save to metadata


        println!(
            "Length of `{name}` (`{file_name}`: `{content_type}`) is {} bytes",
            data.len()
        );


    }

}


#[derive(Template)]
#[template(path = "user_metadata.html")]
pub struct UserMetadataTemplate {
    pub username: String,
    pub uuid: String,
    pub created_at: NaiveDateTime
}

pub async fn get_user_data(jar: CookieJar) -> Result<HtmlTemplate<UserMetadataTemplate>, StatusCode> {

    if let Some(uuid) = jar.get("uuid") {
        let user = get_user_by_uuid(uuid.value().to_string()).await;
        let template = UserMetadataTemplate {
            username: user.username,
            uuid: user.uuid,
            created_at: user.created_at,
        };
        Ok(HtmlTemplate(template))
    } else {
        return Err(StatusCode::NOT_FOUND);
    }
}



#[derive(Deserialize, Debug)]
pub struct UserRegisterReq{
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
        Html(format!("uuid: {}, <a href='/profile'>Go to profile</a>", uuid.value()))
    } else {
        Html("No UUID found in cookies.".to_string())
    }
}


pub async fn user_form(jar: CookieJar) -> Result<HtmlTemplate<UserFormTemplate>, Redirect> {

    if let Some(_uuid) = jar.get("uuid") {
        // TODO check for cookie forgery
        Err(Redirect::temporary("/profile"))
    } else {
        let template = UserFormTemplate{};
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
T: Template
{
    fn into_response(self) -> axum::response::Response {
        match self.0.render() {
            Ok(html) => Html(html).into_response(),
            Err(err) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Failed to render template. Error {err}"),
            ).into_response()
        }
    }
}
}