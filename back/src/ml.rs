pub mod ml {
    use std::{collections::HashMap, env, path::PathBuf};

    use askama::Template;
    use axum::{
        extract::Path,
        response::{Html, IntoResponse},
    };
    use serde::{Deserialize, Serialize};
    use tch::{CModule, Kind, Tensor};

    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }
    pub fn load_model() -> CModule {
        use dotenv::dotenv;
        dotenv().ok();

        // let model_location = env::var("UTILS_DIR").expect("UPLOADS_DIR env var not found");
        // let model_name = env::var("LATEST_MODEL").expect("LATEST_MODEL env var not found");

        let model_location = "./util".to_string();
        let model_name = "jit_cpu_latest.pt".to_string();


        tracing::info!("MODEL FOUND - {}\\{}", model_location, model_name);
        println!("MODEL FOUND - {}\\{}", &model_location, &model_name);

        let model = CModule::load(format!("{}\\{}", model_location, model_name))
            .expect("model should be loadable");

        model
    }




    pub fn load_signal(path: String) -> Result<Vec<f32>, Box<dyn std::error::Error>> {
        println!("{:?}", &path);
        let bytes = std::fs::read(path)?;

        let npy = npyz::NpyFile::new(&bytes[..])?;

        let mut signal: Vec<f32> = Vec::new();

        for number in npy.data::<f32>()? {
            let number = number?;
            signal.push(number);
        }

        Ok(signal)
    }

    pub fn signal_to_tensors(signal: &[f32]) -> Vec<Tensor> {
        let frame_size = 22050;
        let mut tensors = Vec::new();

        for chunk in signal.chunks(frame_size) {
            if chunk.len() == frame_size {
                let tensor = Tensor::from_slice(chunk)
                .reshape(&[1, 1, frame_size as i64])
                .to_kind(Kind::Float)
                .to_device(tch::Device::Cpu);
            tensors.push(tensor);
            }
        }
        tensors
    }

    #[derive(Debug, Serialize, Deserialize)]
    pub struct FrameClassification {
        logits: Vec<f32>,
        propabilities: Vec<f32>,
        class: usize,
        biggest_propability: f32
    }


    pub fn classify_signal(model: CModule, path: String) -> HashMap<usize, FrameClassification> {
        let signal = load_signal(path).expect("Should be valid signal");

        let tensors = signal_to_tensors(&signal);

        let mut results: HashMap<usize, FrameClassification> = HashMap::new();

        for (index, frame) in tensors.iter().enumerate() {
            let logits = model.forward_ts(&[frame]).expect("Should produce output"); // Tensor [1,5]
            let probs = logits.softmax(1, tch::Kind::Float);
            
            let probs_vec: Vec<f32> = probs
            .shallow_clone()
            .view([-1])
            .try_into()
            .expect("Should be valid logits into propabilities"); 
            println!("Propabilities {:?}", probs_vec);
            
            let values: Vec<f32> = logits
            .shallow_clone()
            .view([-1])
            .try_into()
            .unwrap();
            println!("{:?}", &values);

            let (max_index, max_value) = values
            .iter()
            .enumerate()
            .fold((0, f32::MIN), |(max_i, max_v), (i, &v)| {
                if v > max_v {
                    (i, v)
                } else {
                    (max_i, max_v)
                }
            });

            println!("max_index: {}, max_value: {}", max_index, max_value);

            let classification_result = FrameClassification {
                logits: values,
                propabilities: probs_vec,
                class: max_index,
                biggest_propability: max_value
            };

            results.insert(index, classification_result);
            
        } 
    
        results
                
    }

    #[test]
    fn test_classify_signal() {
        classify_signal(load_model(), "./util/test_signal.npy".to_string());

        assert!(true)
    }

    #[test]
    fn test_load_signal() {
        let signal = load_signal("./util/test_signal.npy".to_string()).expect("should work");

        assert_eq!(signal.len(), 308700)
    }


    // #[derive(Template)]
    // #[template(path = "classification_results.html")]
    // pub struct ClassificationResultsTemplate {
    //     classifications: Vec<FrameClassification>
    // }

    pub async fn classify(Path(upload_uuid): Path<String>) -> impl IntoResponse {
        // GET /server_data/transformed_signals/614e96f3-d91b-4734-b3b7-91f7cbc5f764-001018.npy


        let model = load_model();

        tracing::info!("searching for signal in: {}", format!("{}{}/{}.npy", 
        env::var("SERVER_DATA").expect("SERVER_DATA should be reachable"),
         "transformed_signals",
        upload_uuid));

        let classifications = classify_signal(model, 
        format!("{}{}/{}.npy", 
        env::var("SERVER_DATA").expect("SERVER_DATA should be reachable"),
         "transformed_signals",
        upload_uuid));

        // read one frame
        // classify
        // print the class




        Html(format!(
            r#"<div class="job-container" hx-target="this" hx-swap="outerHTML">Class: {:?}</div>"#,
            classifications
        ))
    }

    #[cfg(test)]
    mod tests {

        use std::env;

        use tch::{CModule, Tensor};

        use super::*;


        #[test]
        fn test_libtorch_works() {
            use dotenv::dotenv;
            dotenv().ok();

            let model_location = env::var("UTILS_DIR").expect("UPLOADS_DIR env var not found");
            let model_name = env::var("LATEST_MODEL").expect("LATEST_MODEL env var not found");

            let paths = std::fs::read_dir(format!("{}", model_location)).unwrap();
            for path in paths {
                println!("{}", path.unwrap().path().display())
            }

            println!("{}\\{}", model_location, model_name);

            let model = CModule::load(format!("{}\\{}", model_location, model_name))
                .expect("model should be loadable");

            let input = Tensor::randn(&[1, 1, 22050], (tch::Kind::Float, tch::Device::Cpu));
            let output = model.forward_ts(&[input]).expect("Should produce output");

            println!("{}", output);

            assert!(true)
        }

        #[test]
        fn test_add() {
            assert_eq!(add(1, 2), 3)
        }
    }
}
