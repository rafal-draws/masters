pub mod db_conn {

    use chrono::{Local, NaiveDateTime, Utc};
    use serde::{Deserialize, Serialize};
    use sqlx::{migrate::MigrateDatabase, prelude::FromRow, Pool, Sqlite, SqlitePool};
    use std::env;
    use uuid::Uuid;

    use crate::http::user_http::DeleteStatus;

    #[derive(Debug)]
    pub enum AuthError {
        UUIDError(String),
    }

    pub enum SqlError {
        UploadQueryError(String),
    }

    #[derive(FromRow, Debug, Serialize)]
    pub struct User {
        pub id: i64,
        pub username: String,
        pub uuid: String,
        pub created_at: NaiveDateTime, // pub songs: Vec<String>
    }

    impl User {
        pub async fn new(username: String) -> Self {
            let uuid = Uuid::new_v4().to_string();

            let database_user = Self::create_user(username, uuid).await;

            Self {
                id: database_user.id,
                uuid: database_user.uuid,
                username: database_user.username,
                created_at: Utc::now().naive_utc(), // songs: vec![],
            }
        }

        async fn create_user(username: String, uuid: String) -> User {
            // TODO wrap in option
            let db = SqlitePool::connect(
                &env::var("DATABASE_URL")
                    .expect("Database URL should be reachable when creating user"),
            )
            .await
            .expect("Should be valid sqlite pool");

            let mut tx = db.begin().await.expect("should create transaction");
            let query = sqlx::query(
                "INSERT INTO user (username, uuid, created_at) values (?, ?, CURRENT_TIMESTAMP)",
            )
            .bind(&username)
            .bind(&uuid)
            .execute(&mut *tx)
            .await
            .expect("Should execute transaction creating a user");

            println!("User added successfully: {:?}", query);

            let user_struct: User = sqlx::query_as::<_, User>(
                "SELECT id, username, uuid, created_at from user where uuid = $1",
            )
            .bind(uuid)
            .fetch_one(&mut *tx)
            .await
            .expect("User should exist at this point");

            tx.commit().await.expect("Transaction should be closed");

            user_struct
        }
    }

    #[derive(FromRow, Debug, Deserialize, Serialize)]
    pub struct Upload {
        pub id: i64,
        pub user_uuid: String,
        pub upload_uuid: String,
        pub file_name: String,
        pub added: NaiveDateTime,
    }

    pub fn get_default_upload() -> Vec<Upload> {
        let mut default_vec = Vec::new();

        default_vec.insert(
            0,
            Upload {
                id: 0,
                upload_uuid: "insert".to_string(),
                user_uuid: "your first".to_string(),
                file_name: "song".to_string(),
                added: Local::now().naive_local(),
            },
        );

        default_vec
    }

    pub async fn get_all_uploads(user_uuid: &String) -> Result<Vec<Upload>, SqlError> {
        let pool = get_pool().await;
        let mut tx = pool.begin().await.expect("should create transaction");

        let uploads_vec = sqlx::query_as::<_, Upload>(
            "SELECT DISTINCT id, user_uuid, upload_uuid, file_name, added from upload where user_uuid = $1"
        )
        .bind(user_uuid)
        .fetch_all(&mut *tx)
        .await;

        tx.commit().await.expect("Transaction should be closed");

        match uploads_vec {
            Ok(v) => {
                tracing::debug!("{:?}", v);
                Ok(v)
            }
            Err(e) => Err(SqlError::UploadQueryError(format!(
                "Uploads couldn't be fetched. {} \n {}",
                user_uuid, e
            ))),
        }
    }

    pub async fn insert_upload_to_db(user_uuid: &String, file_name: &String) -> Upload {
        let pool = get_pool().await;
        let upload_uuid = Uuid::new_v4().to_string();

        let mut tx = pool.begin().await.expect("should create transaction");
        let query = sqlx::query("INSERT INTO upload (user_uuid, upload_uuid, file_name, added) values (?, ?, ?, CURRENT_TIMESTAMP)")
        .bind(user_uuid)
        .bind(&upload_uuid)
        .bind(file_name)
        .execute(&mut *tx)
        .await
        .expect(&format!("Should insert record for {} {}", user_uuid, file_name));

        println!("Upload added successfully: {:?}", query);

        let user_struct: Upload = sqlx::query_as::<_, Upload>(
            "SELECT id, user_uuid, upload_uuid, file_name, added from upload where upload_uuid = $1"
        )
        .bind(upload_uuid)
        .fetch_one(&mut *tx)
        .await
        .expect("Insert should exist at this point");

        tx.commit().await.expect("Transaction should be closed");

        user_struct
    }

    pub async fn delete_upload(upload_uuid: String, user_uuid: String) -> DeleteStatus {
        let pool = get_pool().await;

        let mut tx = pool.begin().await.expect("should create transaction");

        let row_delete =
            sqlx::query("DELETE FROM upload where upload_uuid = $1 and user_uuid = $2")
                .bind(&upload_uuid)
                .bind(&user_uuid)
                .execute(&mut *tx)
                .await
                .expect("Delete be possible at this point");

        match tx.commit().await {
            Ok(a) => {
                tracing::debug!("{:?}, {:?}", a, row_delete);
                DeleteStatus {
                    upload_uuid: upload_uuid,
                    user_uuid: user_uuid,
                    status: true,
                }
            }
            Err(e) => DeleteStatus {
                upload_uuid: upload_uuid,
                user_uuid: user_uuid,
                status: false,
            },
        }
    }

    pub async fn get_pool() -> Pool<Sqlite> {
        let db = SqlitePool::connect(
            &env::var("DATABASE_URL").expect("Database URL should be reachable when creating user"),
        )
        .await
        .expect("Should be valid sqlite pool");
        db
    }

    pub async fn get_user_by_uuid(uuid: &String) -> Result<User, AuthError> {
        sqlx::query_as_unchecked!(User, "select * from user where uuid = ?", uuid)
            .fetch_one(&get_pool().await)
            .await
            .map_err(|_| AuthError::UUIDError(uuid.to_string()))
    }

    pub async fn create_db() {
        let url = &env::var("DATABASE_URL").expect("DATABASE_URL Should exist at this point");
        if !Sqlite::database_exists(url).await.unwrap_or(false) {
            match Sqlite::create_database(url).await {
                Ok(_) => println!("database was set up successfully at {}", url),
                Err(e) => panic!("Error: {}", e),
            }
        } else {
            println!("Database already exists")
        }
    }
}
