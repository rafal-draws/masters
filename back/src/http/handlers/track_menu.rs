use askama::Template;
use axum::{extract::Path, response::IntoResponse};

use crate::{
    http::handlers::HtmlTemplate,
    ml::ml::{instantiate_models, Feature, FeatureDetail, SongClassificationResult},
};

#[derive(Template)]
#[template(path = "track_menu.html")]
pub struct TrackMenu {
    pub song_classification_result: SongClassificationResult,
    pub upload_name: String,
    pub cum_class: Vec<String>,
    pub features: Vec<FeatureDetail>
}

pub async fn track_menu(Path(upload_name): Path<String>) -> impl IntoResponse {
    let mut models = instantiate_models(Feature::all());

    let song_classificaiton_result = SongClassificationResult::new(&mut models, upload_name.clone());

    let cum_class: Vec<String> = song_classificaiton_result.cum_classification.clone().iter().map(|x| format!("{:.2}%", x * 100.0)).collect();

    let features: Vec<FeatureDetail> = song_classificaiton_result.get_features_formatted_for_path();

    let template = TrackMenu {
        upload_name: upload_name,
        song_classification_result: song_classificaiton_result,
        cum_class: cum_class,
        features: features
    };

    HtmlTemplate(template)
}
