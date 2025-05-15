-- Add migration script here

--Up
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY NOT NULL,
    uuid VARCHAR(36) NOT NULL,
    username VARCHAR(250) NOT NULL,
    created_at DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS upload (
    id INTEGER PRIMARY KEY NOT NULL,
    user_uuid VARCHAR(36) NOT NULL,
    file_name VARCHAR(250) NOT NULL,
    added DATETIME NOT NULL
)