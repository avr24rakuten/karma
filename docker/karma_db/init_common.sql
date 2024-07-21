CREATE DATABASE IF NOT EXISTS karma;
USE karma;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT,
    user VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(512) NOT NULL,
    admin BOOLEAN NOT NULL DEFAULT FALSE,
    steward BOOLEAN NOT NULL DEFAULT FALSE,
    reader BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (user),
    INDEX user_id_index (user_id)
);

CREATE TABLE api_log_perf (
    call_datetime DATETIME NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    duration_ms INT NOT NULL,
    status_code INT NOT NULL,
    PRIMARY KEY (endpoint, call_datetime)
);
