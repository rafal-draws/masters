pub mod db_conn {

    use std::env;
    use sqlx::{migrate::MigrateDatabase, prelude::FromRow, Pool, Sqlite, SqlitePool};
    use chrono::{NaiveDateTime, Utc};
    use serde::{Deserialize, Serialize};
    use uuid::Uuid;

    #[derive(FromRow, Debug, Serialize)]
    pub struct User {
        pub id: i64,
        pub username: String,
        pub uuid: String,
        pub created_at: NaiveDateTime
        // pub songs: Vec<String>
    }

    impl User {
        pub async fn new(username: String) -> Self {
            let uuid = Uuid::new_v4().to_string();
            
            let database_user = Self::create_user(username, uuid).await;

            Self {
                id: database_user.id,
                uuid: database_user.uuid,
                username: database_user.username,
                created_at: Utc::now().naive_utc()
                // songs: vec![],
            }
        }

        async fn create_user(username: String, uuid: String) -> User {
            // TODO wrap in option
            let db = SqlitePool::connect(
                &env::var("DATABASE_URL")
                .expect("Database URL should be reachable when creating user"))
                .await
                .expect("Should be valid sqlite pool");

            let mut tx = db.begin().await.expect("should create transaction");
            let query = sqlx::query("INSERT INTO user (username, uuid, created_at) values (?, ?, CURRENT_TIMESTAMP)")
            .bind(&username)
            .bind(&uuid)
            .execute(&mut *tx)
            .await
            .expect("Should execute transaction creating a user");

            println!("User added successfully: {:?}", query);

            let user_struct: User = sqlx::query_as::<_, User>(
                "SELECT id, username, uuid, created_at from user where uuid = $1"
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
    struct Upload {
        id: i64,
        uuid: String,
        file_name: String,
        added: NaiveDateTime
    }


    pub async fn get_pool() -> Pool<Sqlite>{
        let db = SqlitePool::connect(
            &env::var("DATABASE_URL")
            .expect("Database URL should be reachable when creating user"))
            .await
            .expect("Should be valid sqlite pool");
        db
    }

    pub async fn get_user_by_uuid(uuid: String) -> User {
        sqlx::query_as_unchecked!(
            User,
            "select * from user where uuid = ?",
            uuid
        )
        .fetch_one(&get_pool().await)
        .await
        .expect("Should be fetchable")
    }

    pub async fn create_db() {
        let url = &env::var("DATABASE_URL").expect("DATABASE_URL Should exist at this point");
        if !Sqlite::database_exists(url).await.unwrap_or(false){
            match Sqlite::create_database(url).await {
                Ok(_) => println!("database was set up successfully at {}", url),
                Err(e) => panic!("Error: {}", e)
            }
        } else {
            println!("Database already exists")
        }
    }
}