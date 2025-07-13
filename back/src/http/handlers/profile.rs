use askama::Template;
use axum_extra::extract::CookieJar;
use reqwest::StatusCode;

use crate::{db::db_conn::{get_all_uploads, get_default_upload, get_user_by_uuid, Upload}, http::handlers::HtmlTemplate};



#[derive(Template)]
    #[template(path = "user_metadata.html")]
    pub struct UserMetadataTemplate {
        pub username: String,
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
                uploads: uploads,
            };
            Ok(HtmlTemplate(template))
        } else {
            // TODO ask user to enter incognito / clear cache
            return Err(StatusCode::NOT_FOUND);
        }
    }