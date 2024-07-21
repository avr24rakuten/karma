USE karma;

INSERT INTO users (user, hashed_password, admin, steward, reader)
VALUES ('admin', '$2b$12$4U2Br18jSvXNHp/FKniQXuJ5KwJ299e3NfozbAtyqzYfeBQWgxD0i', true, false, false);

INSERT INTO users (user, hashed_password, admin, steward, reader)
VALUES ('steward', '$2b$12$l6rdOtvBIddb0rcXskGZYOiVcrNc0qtko90x.Fwlb1h5wbx0kn56a', false, true, false);

INSERT INTO users (user, hashed_password, admin, steward, reader)
VALUES ('reader', '$2b$12$mNfKY077HWV8.WVQiZr3C.QE8L..753pC0duTXtH9RQV7VVYSR4b6', false, false, true);

INSERT INTO users (user, hashed_password, admin, steward, reader)
VALUES ('admin_steward', '$2b$12$pQWUbEHEVVQcneinO5k0UeMW1yTncg5CQTr5HYwiIt8DWFy0/btE.', true, true, false);

INSERT INTO users (user, hashed_password, admin, steward, reader)
VALUES ('admin_reader', '$2b$12$pHMUnOa1pNiARy6nZ5jKqOY4mi5X.g0BuJCqthkhsKwlAmOg/sTda', true, false, true);

INSERT INTO users (user, hashed_password, admin, steward, reader)
VALUES ('delete', '$2b$12$VfHkXXcuHrgqK9lxn9kB.ug8YQlp/Jv1U0oWCWchfi1mOBSBFs/0m', false, false, false);