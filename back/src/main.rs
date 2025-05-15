extern crate dotenv;

mod http;
mod db;

use back::config::{self, create_upload_dir};

use db::db_conn;
use dotenv::dotenv;
use axum::extract::DefaultBodyLimit;

use axum::routing::{get, post};
use axum::Router;
use http::user_http::{get_user_data, register_user, upload_track, user_form, user_registered};

#[tokio::main ]
async fn main() -> Result<(), Box<std::io::Error>>{

    dotenv().ok();
    db_conn::create_db().await;
    create_upload_dir().await;

    let pool = db_conn::get_pool().await;

    sqlx::migrate!("./migrations").run(&pool)
    .await
    .expect("Migration should be possible");

    
    let app = app()
    .layer(config::create_cors_layers())
    .layer(DefaultBodyLimit::max(250 * 1024 * 1024));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3000")
    .await
    .unwrap();

    println!("listening on http://127.0.0.1:3000");
    axum::serve(listener, app).await.unwrap();

    Ok(())

}

fn app() -> Router {
    Router::new()
    .route("/", get(user_form))
    .route("/register", post(register_user).get(user_registered))
    .route("/profile", get(get_user_data))
    .route("/upload", post(upload_track))
}


    

#[cfg(test)]
mod tests {
    use axum::{body::Body, extract::Request, http::StatusCode};
    use tower::ServiceExt;

    use super::*;
    
    #[tokio::test]
    async fn test_main() {
        let response = app()
            .oneshot(
                Request::builder()
                .uri("/register")
                .body(Body::empty())
                .unwrap()
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);
    }
}