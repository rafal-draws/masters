

pub mod ml {


pub fn add(a: i32, b:i32) -> i32 {
    a + b
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