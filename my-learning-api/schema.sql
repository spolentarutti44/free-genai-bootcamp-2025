DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS study_activities;
DROP TABLE IF EXISTS study_sessions;
DROP TABLE IF EXISTS words;
DROP TABLE IF EXISTS word_groups;
DROP TABLE IF EXISTS word_review_items;

CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    words_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT
);

CREATE TABLE study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    study_activity_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
);

CREATE TABLE words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kanji TEXT NOT NULL,
    romaji TEXT NOT NULL,
    salish TEXT NOT NULL,
    navajo TEXT NOT NULL,
    english TEXT NOT NULL,
    parts TEXT -- JSON
);

CREATE TABLE word_groups (
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    PRIMARY KEY (word_id, group_id)
);

CREATE TABLE word_review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    study_session_id INTEGER NOT NULL,
    correct BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id),
    FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
); 