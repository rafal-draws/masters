extern crate dotenv;

mod db;
mod http;
mod ml;

use std::time::Duration;

use back::config::{self, clear_server_data, create_server_data_dirs, create_upload_dir};

use axum::extract::DefaultBodyLimit;
use db::db_conn::{self, drop_all_uploads};
use dotenv::dotenv;


use ml::ml::classify;
use tokio::time::sleep;
use tower_http::services::ServeDir;

use axum::routing::{get, post};
use axum::Router;
use http::user_http::{
    delete_upload_http, get_track_details, get_user_data, register_user, send_to_classification,
    upload_track, user_form, user_registered,
};
use tracing_subscriber::fmt;

#[tokio::main]
async fn main() -> Result<(), Box<std::io::Error>> {
    dotenv().ok();
    
    db_conn::create_db().await;

    clear_server_data().await.unwrap();
    tracing::info!("server_data cleared!");
    drop_all_uploads().await.unwrap();
    tracing::info!("uploads in db cleared!");
    sleep(Duration::from_secs(1 * 60)).await;
    
    let subscriber = fmt()
    .with_line_number(true)
    .with_file(true)
    .finish();

    tracing::subscriber::set_global_default(subscriber).expect("setting tracing default failed");

    create_server_data_dirs("server_data")?;
    tracing::info!("Directories created");
 

    db_conn::create_db().await;

    create_upload_dir().await;

    let pool = db_conn::get_pool().await;

    sqlx::migrate!("./migrations")
        .run(&pool)
        .await
        .expect("Migration should be possible");

    let app = app()
        .layer(config::create_cors_layers())
        .layer(DefaultBodyLimit::max(250 * 1024 * 1024));

    let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();

    println!("listening on {:?}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();

     

    Ok(())
}

fn app() -> Router {
    tracing::info!("SETUP - CREATING ENDPOINTS");
    Router::new()
        .route("/", get(user_form))
        .route("/register", post(register_user).get(user_registered))
        .route("/profile", get(get_user_data))
        .route("/upload", post(upload_track))
        .route("/delete/{upload_uuid}", post(delete_upload_http))
        .route("/track/{upload_uuid}", get(get_track_details))
        .route(
            "/classification/{upload_uuid}",
            post(send_to_classification),
        ).route(
            "/classify/{upload_uuid}",
            post(classify),
        )
        .nest_service("/server_data", ServeDir::new("server_data"))
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
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);
    }
}
