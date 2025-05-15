pub mod config {
    use std::{env, io::ErrorKind};

    use axum::http::{HeaderValue, Method};
    use tower_http::cors::CorsLayer;

    
    pub async fn create_upload_dir() {
        
    let dir = env::var("UPLOADS_DIR").expect("UPLOADS DIR env var not found");

    let _upload_dir = match tokio::fs::create_dir_all(&dir).await {
        Ok(_) => Ok(()),
        Err(e) if e.kind() == ErrorKind::AlreadyExists => Ok(()), // Silently ignore
        Err(e) => Err(Box::new(e)), // Pass up other errors
    }.expect("Should create directory");
    }

    pub fn create_cors_layers() -> CorsLayer {
        
    CorsLayer::new()
    .allow_origin("http://localhost:3000".parse::<HeaderValue>().unwrap())
    .allow_methods([Method::GET, Method::POST])

    }

}