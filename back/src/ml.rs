pub mod ml {
    use std::{collections::{BTreeMap, HashMap}, env};

    // use askama::Template;
    use axum::{
        extract::Path,
        response::{Html, IntoResponse},
    };
    use serde::{Deserialize, Serialize};
    use tch::{CModule, Kind, Tensor};


    
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

    pub async fn load_signal(signal_path: String) -> Result<Vec<f32>, Box<dyn std::error::Error>> {
        tracing::info!("load_signal fun - looking at {}", &signal_path);


        let bytes = std::fs::read(signal_path)?;

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

    #[derive(Debug, Serialize, Deserialize, Clone)]
    pub struct FrameClassification {
        logits: Vec<f32>,
        propabilities: Vec<f32>,
        class: usize,
        biggest_propability: f32,
    }

    pub async fn classify_signal(
        model: CModule,
        path: String,
    ) -> HashMap<usize, FrameClassification> {
        let signal = load_signal(path).await.expect("Should be valid signal");

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

            let values: Vec<f32> = logits.shallow_clone().view([-1]).try_into().unwrap();
            println!("{:?}", &values);

            let (max_index, max_value) =
                values
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
                biggest_propability: max_value,
            };

            results.insert(index, classification_result);
        }

        results
    }

    #[tokio::test]
    async fn test_classify_signal() {
        classify_signal(load_model(), "./util/test_signal.npy".to_string()).await;

        assert!(true)
    }

    #[tokio::test]
    async fn test_load_signal() {
        let signal = load_signal("./util/test_signal.npy".to_string())
            .await
            .expect("should work");

        assert_eq!(signal.len(), 308700)
    }

    // #[derive(Template)]
    // #[template(path = "classification_results.html")]
    // pub struct ClassificationResultsTemplate {
    //     classifications: Vec<FrameClassification>
    // }

    pub async fn classify(Path(signal): Path<String>) -> impl IntoResponse {

        let model = load_model();

        tracing::info!(
            "searching for signal in: {}",
            format!(
                "{}{}/{}",
                env::var("SERVER_DATA").expect("SERVER_DATA should be reachable"),
                "transformed_signals",
                &signal
            )
        );

        let classifications = classify_signal(
            model,
            format!(
                "{}{}/{}",
                env::var("SERVER_DATA").expect("SERVER_DATA should be reachable"),
                "transformed_signals",
                signal
            ),
        )
        .await;

        let mut class_0_prop: f32 = 0.0;
        let mut class_0_median: Vec<f32> = Vec::new();

        let mut class_1_prop: f32 = 0.0;
        let mut class_1_median: Vec<f32> = Vec::new();

        let mut class_2_prop: f32 = 0.0;
        let mut class_2_median: Vec<f32> = Vec::new();
        
        let mut class_3_prop: f32 = 0.0;
        let mut class_3_median: Vec<f32> = Vec::new();

        let mut class_4_prop: f32 = 0.0;
        let mut class_4_median: Vec<f32> = Vec::new();

        let mut frame_classes = BTreeMap::new();

        let mut classifications_count: HashMap<usize, u8> = HashMap::new();

        let classifications_copy = classifications.clone();



        for (key, val) in classifications_copy.iter() {
            match val.class {
                0 => {
                    class_0_prop += val.biggest_propability;
                    class_0_median.push(val.biggest_propability);
                    frame_classes.insert(key, val.class);
                    classifications_count.entry(0).and_modify(|e| *e += 1).or_insert(0);
                }
                1 => {
                    class_1_prop += val.biggest_propability;
                    class_1_median.push(val.biggest_propability);
                    frame_classes.insert(key, val.class);
                    classifications_count.entry(1).and_modify(|e| *e += 1).or_insert(0);
                }
                2 => {
                    class_2_prop += val.biggest_propability;
                    class_2_median.push(val.biggest_propability);
                    frame_classes.insert(key, val.class);
                    classifications_count.entry(2).and_modify(|e| *e += 1).or_insert(0);
                },
                3 => {
                    class_3_prop += val.biggest_propability;
                    class_3_median.push(val.biggest_propability);
                    frame_classes.insert(key, val.class);
                    classifications_count.entry(3).and_modify(|e| *e += 1).or_insert(0);
                },
                4 => {
                    class_4_prop += val.biggest_propability;
                    class_4_median.push(val.biggest_propability);
                    frame_classes.insert(key, val.class);
                    classifications_count.entry(4).and_modify(|e| *e += 1).or_insert(0);
                },
                _ => tracing::info!(
                    "Couldn't read biggest propability from classification for {}",
                    &signal
                ),
            };
        }

        // let class_0_avg: f32 = class_0_prop / frame_classes.len() as f32;
        // let class_1_avg: f32 = class_1_prop / frame_classes.len() as f32;
        // let class_2_avg: f32 = class_2_prop / frame_classes.len() as f32;
        // let class_3_avg: f32 = class_3_prop / frame_classes.len() as f32;
        // let class_4_avg: f32 = class_4_prop / frame_classes.len() as f32;

        let class_0_med_val = median(&mut class_0_median);
        let class_1_med_val = median(&mut class_1_median);
        let class_2_med_val = median(&mut class_2_median);
        let class_3_med_val = median(&mut class_3_median);
        let class_4_med_val = median(&mut class_4_median);
        

        Html(format!(
            r#"<div class="job-container" hx-target="this" hx-swap="outerHTML">
            <div>Class "Rock"<br>median: {:?}<br>prop: {:?}</div>
            <div>Class "Hip-Hop"<br>median: {:?}<br>prop: {:?}</div>
            <div>Class "Electronic"<br>median: {:?}<br>prop: {:?}</div>
            <div>Class "Pop"<br>median: {:?}<br>prop: {:?}</div>
            <div>Class "Classical"<br>median: {:?}<br>prop: {:?}</div>



            <div>Frame numbers and classifications <br> {:?} <br></div>
            
            <div>Classifications count <br> {:?} <br></div>
            </div>"#,
            class_0_med_val, class_0_prop,
            class_1_med_val, class_1_prop,
            class_2_med_val, class_2_prop,
            class_3_med_val, class_3_prop,
            class_4_med_val, class_4_prop,
            frame_classes, classifications_count
        ))
    }


    pub fn median(data: &mut Vec<f32>) -> Option<f32> {
         let len = data.len();
    if len == 0 {
        return None;
    }
    
    data.sort_by(|a, b| a.partial_cmp(b).unwrap());
    
    let mid = len / 2;
    if len % 2 == 0 {
        Some((data[mid - 1] + data[mid]) / 2.0)
    } else {
        Some(data[mid])
    }

    }
 
    #[cfg(test)]
    mod tests {

        use std::env;

        use tch::{CModule, Tensor};


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

       
    }
}
