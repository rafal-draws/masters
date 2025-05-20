

pub mod ml {
    use axum::{extract::Path, response::{Html, IntoResponse}};



pub fn add(a: i32, b:i32) -> i32 {
    a + b
}


pub fn load_signal(path: String) -> Result<Vec<f32>, Box<dyn std::error::Error>> {
    let bytes = std::fs::read("./util/test_signal.npy")?;

    let npy = npyz::NpyFile::new(&bytes[..])?;

    let mut signal: Vec<f32> = Vec::new();

    for number in npy.data::<f32>()? {
        let number = number?;
        signal.push(number);
    }

    Ok(signal)

}

#[test]
fn test_load_signal() {
    let signal = load_signal("./util/test_signal.npy".to_string()).expect("should work");

    assert_eq!(signal.len(), 308700)
}

pub async fn classify(
        Path(upload_uuid): Path<String>
    ) -> impl IntoResponse {
// GET /server_data/transformed_signals/614e96f3-d91b-4734-b3b7-91f7cbc5f764-001018.npy
// read one frame
// classify
// print the class

        

    Html(format!(r#"<div class="job-container" hx-target="this" hx-swap="outerHTML">Class: {}</div>"#,upload_uuid))
}




    #[cfg(test)]
    mod tests{

        use std::env;

        use tch::{CModule, Tensor};

        use super::*;
        fn test_file_load() {

            assert!(true)
        }


        #[test]
        fn test() {
            
            use dotenv::dotenv;
            dotenv().ok();

            let model_location = env::var("UTILS_DIR").expect("UPLOADS_DIR env var not found");
            let model_name = env::var("LATEST_MODEL").expect("LATEST_MODEL env var not found");

            let paths = std::fs::read_dir(format!("{}", model_location)).unwrap();
            for path in paths {
                println!("{}", path.unwrap().path().display())
            }

            println!("{}\\{}", model_location, model_name);

            let model = CModule::load(format!("{}\\{}", model_location, model_name)).expect("model should be loadable");

            let input = Tensor::randn(&[1, 1, 22050], (tch::Kind::Float, tch::Device::Cpu));
            let output = model.forward_ts(&[input]).expect("Should produce output");

            println!("{}", output);

            assert!(true)
        }

        #[test]
        fn test_add() {
            assert_eq!(add(1,2), 3)
        }
    }

}