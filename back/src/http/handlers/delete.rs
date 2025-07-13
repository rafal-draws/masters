use askama::Template;
use axum::{extract::Path, response::IntoResponse};
use axum::http::StatusCode;
use axum_extra::extract::CookieJar;

use crate::{db::db_conn::delete_upload_db, http::handlers::HtmlTemplate};




#[derive(Template)]
    #[template(path = "delete_status.html")]
    pub struct DeleteStatus {
        pub upload_uuid: String,
        pub user_uuid: String,
        pub status: bool,
    }

    pub async fn delete_upload(
        Path(upload_uuid): Path<String>,
        jar: CookieJar,
    ) -> impl IntoResponse {
        if let Some(uuid) = jar.get("uuid") {
            let result = delete_upload_db(upload_uuid.clone(), uuid.value().to_string()).await;
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