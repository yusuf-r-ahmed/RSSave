CREATE TABLE IF NOT EXISTS feed_templates (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    headers TEXT NOT NULL
);

INSERT INTO feed_templates (name, headers) 
VALUES ('Test', '1,2,3');