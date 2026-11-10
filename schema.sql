-- Reference schema. SQLAlchemy models initialise the application tables.
CREATE TABLE topics (id INTEGER PRIMARY KEY, name VARCHAR(120) NOT NULL UNIQUE, description TEXT NOT NULL);
CREATE TABLE questions (id INTEGER PRIMARY KEY, topic_id INTEGER NOT NULL REFERENCES topics(id), subtopic VARCHAR(100), question TEXT NOT NULL UNIQUE, options JSON NOT NULL, correct_index INTEGER NOT NULL CHECK(correct_index BETWEEN 0 AND 3), explanation TEXT NOT NULL, difficulty VARCHAR(20), source_url VARCHAR(500), is_approved BOOLEAN DEFAULT TRUE);
CREATE TABLE lesson_progress (id INTEGER PRIMARY KEY, learner VARCHAR(80), topic_name VARCHAR(120), completed BOOLEAN DEFAULT FALSE);
CREATE TABLE quiz_attempts (id INTEGER PRIMARY KEY, learner VARCHAR(80), topic_name VARCHAR(120), total INTEGER, correct INTEGER, accuracy FLOAT, points INTEGER NOT NULL DEFAULT 0);
CREATE TABLE user_questions (id INTEGER PRIMARY KEY, learner VARCHAR(80), topic_name VARCHAR(120), subtopic VARCHAR(100), question TEXT, options JSON, correct_index INTEGER, explanation TEXT, difficulty VARCHAR(20));


CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(40) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    is_guest BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

