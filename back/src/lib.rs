pub mod config {
    use std::{env, fs, io::{self, ErrorKind}, path::Path};

    use axum::http::{HeaderValue, Method};
    use tower_http::cors::CorsLayer;

    pub async fn create_upload_dir() {
        let dir = env::var("UPLOADS_DIR").expect("UPLOADS DIR env var not found");

        let _upload_dir = match tokio::fs::create_dir_all(&dir).await {
            Ok(_) => Ok(()),
            Err(e) if e.kind() == ErrorKind::AlreadyExists => Ok(()), // Silently ignore
            Err(e) => Err(Box::new(e)),                               // Pass up other errors
        }
        .expect("Should create directory");
    }

    pub fn create_cors_layers() -> CorsLayer {
        CorsLayer::new()
            .allow_origin("http://localhost:3000".parse::<HeaderValue>().unwrap())
            .allow_methods([Method::GET, Method::POST])
    }

    pub fn create_server_data_dirs(base: &str) -> std::io::Result<()> {
        let folders = [
            "",
            "chroma",
            "mels",
            "mfcc",
            "power",
            "slices",
            "transformed_signals",
            "uploads",
            "util",
            "videos",
        ];

        for folder in &folders {
            let path = if folder.is_empty() {
                Path::new(base).to_path_buf()
            } else {
                Path::new(base).join(folder)
            };
            std::fs::create_dir_all(path)?;
        }

        Ok(())
    }

    pub async fn clear_server_data() -> io::Result<()> {
    let base_path = Path::new(".server_data");

    if base_path.exists() {
        for entry in fs::read_dir(base_path)? {
            let entry = entry?;
            let path = entry.path();

            if path.is_dir() {
                for inner_entry in fs::read_dir(&path)? {
                    let inner_entry = inner_entry?;
                    let inner_path = inner_entry.path();

                    if inner_path.is_dir() {
                        fs::remove_dir_all(&inner_path)?; 
                    } else {
                        fs::remove_file(&inner_path)?; 
                    }
                }
            } else {
                fs::remove_file(&path)?;
            }
        }
    }

    Ok(())
}
}
