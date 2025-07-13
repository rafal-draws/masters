use std::{env, path::Path};

use askama::Template;
use axum::extract::Multipart;
use axum_extra::extract::CookieJar;
use reqwest::StatusCode;
use tokio::{fs::File, io::AsyncWriteExt};
use tracing::{debug, info};

use crate::{db::db_conn::{get_user_by_uuid, insert_upload_to_db}, http::handlers::HtmlTemplate};



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

            let server_data = env::var("SERVER_DATA").expect("SERVER_DATA env var not found");
        
            let dir = Path::new(&server_data).join("uploads");


            let name = field.name().unwrap().to_string();
            let file_name = field.file_name().unwrap().to_string();

            debug!("name: {:?}", &name);

            debug!("filename: {:?}", &file_name);

            let file_name_normalized = file_name
            .to_lowercase()
            .replace(" ", "")
            .replace("-", "")
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "")
            .replace("\"", "")
            .replace("]", "")
            .replace("[", "")
            .replace("'", "");


            debug!("filename: {:?}", &file_name_normalized);

            let suffix = &file_name_normalized
                .split(".")
                .into_iter()
                .last()
                .expect("Should contain suffix");

            match *suffix {
                "mp3" | "wav" => println!("file is .wav or mp3"),
                _ => return Err(StatusCode::FORBIDDEN),
            }

            let data = field.bytes().await.unwrap();

            let upload = insert_upload_to_db(&user.uuid, &file_name_normalized).await;
            tracing::info!("UPLOADING");
            
            
            tracing::info!(
                "{}",
                format!(
                    "{}/{}-{}",
                    dir.display(),
                    upload.upload_uuid,
                    upload.file_name,
                )
            );
            let mut file = File::create(format!(
                "{}/{}-{}",
                dir.display(),
                upload.upload_uuid,
                upload.file_name
            ))
            .await
            .expect("Should create file under specified path");

            let _ = file.write_all(&data).await.unwrap();
            
            info!("Starting request for processing!");

        
            tracing::info!(
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