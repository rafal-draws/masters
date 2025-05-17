

// pub mod ml {

    

// pub fn add(a: i32, b:i32) -> i32 {
//     a + b
// }

//     #[cfg(test)]
//     mod tests{

//         use std::env;

//         use tch::{CModule, Tensor};

//         use super::*;
//         #[test]
//         fn test() {
//             let model_location = env::var("UPLOADS_DIR").expect("UPLOADS_DIR env var not found");
//             let model_name = env::var("LATEST_MODEL").expect("LATEST_MODEL env var not found");
//             let model = CModule::load(format!("{}/{}", model_location, model_name)).expect("model should be loadable");

//             let input = Tensor::randn(&[1, 22050], (tch::Kind::Float, tch::Device::Cpu));
//             let output = model.forward_ts(&[input]).expect("Should produce output");

//             println!(output);

//             assert(true)
//         }

//         #[test]
//         fn test_add() {
//             assert_eq!(add(1,2), 3)
//         }
//     }

// }