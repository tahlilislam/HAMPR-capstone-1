-- from the terminal run:
-- psql postgress < capstone1_schema.sql

DROP DATABASE IF EXISTS sample_capstone1;
CREATE DATABASE sample_capstone1;

\c sample_capstone1

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    age INT,
    ethnicity VARCHAR(255),
    profession_or_in_school VARCHAR(255),
    financial_status_range VARCHAR(255),
    location_general VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-----INTITAL SURVEY SCHEMA-------
CREATE TABLE initial_survey (
    initial_survey_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE initial_questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL, --not sure if its necessary, maybe multiple choice or short ans
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    initial_survey_id INT REFERENCES initial_survey

);

CREATE TABLE initial_responses (
    response_id SERIAL PRIMARY KEY,
    answer_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    initial_survey_id INT REFERENCES initial_survey,
    user_id INT REFERENCES users,
    question_id INT REFERENCES initial_questions
);

----POST REFLECTIVE SURVEY RESULTS schema------

CREATE TABLE post_reflective_survey (
    post_survey_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    initial_survey_id INT REFERENCES initial_survey,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post_reflective_questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL, -- e.g., multiple_choice, short_ans
    post_survey_id INT REFERENCES post_reflective_survey,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE post_reflective_responses (
    response_id SERIAL PRIMARY KEY,
    answer_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    post_survey_id INT REFERENCES post_reflective_survey,
    user_id INT REFERENCES users,
    question_id INT REFERENCES post_reflective_questions
);

---JOURNAL entries schema-----
CREATE TABLE journal_entries (
    entry_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users,
    entry_text TEXT NOT NULL,
    entry_date DATE DEFAULT CURRENT_DATE, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
---needs modified date----

---TEXT CLASSIFICATION RESULTS schema-----
CREATE TABLE text_classification_results (
    result_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users,
    entry_id INT REFERENCES journal_entries, 
    classification_result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
--- 2 entries after modified---
---keep the most updated info---
--- Can do historical information---
--- can store previous results but not show it--

---SUGGESTED GOALS schema---
CREATE TABLE suggested_goals (
    suggested_goal_id SERIAL PRIMARY KEY,
    suggested_goal_text TEXT NOT NULL,
    frequency INT, -- Specify frequency for suggested goals
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

---GOALS schema-------
CREATE TABLE goals (
    goal_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users,
    suggested_goal_id INT REFERENCES suggested_goals, -- Reference to suggested goals, NULL if user creates own goal
    user_defined_goal TEXT, -- User-defined goal text, NULL if choosing from suggested goals
    frequency INT, 
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    completed BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ---modified date, if frequency or goal changed
);
