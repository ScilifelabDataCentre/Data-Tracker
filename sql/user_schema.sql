CREATE SCHEMA IF NOT EXISTS users;

CREATE TYPE user_permissions AS enum('Standard', 'Steward', 'Admin');
-- Standard - can own datasets
-- Steward - Generator + can modify and delete datasets
-- Admin - Steward + can change permissions for users


CREATE TABLE IF NOT EXISTS users.users (
    id integer PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    given_name          varchar(100)        DEFAULT NULL,
    email               varchar(100)        UNIQUE NOT NULL,
    affiliation         varchar(100)        DEFAULT NULL,
    country             varchar(100)        DEFAULT NULL,
    auth_identity       varchar(100)        UNIQUE,
    permission          user_permissions    NOT NULL DEFAULT 'Standard'
);

CREATE TABLE IF NOT EXISTS users.auth_keys (
    id integer PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    system_name          varchar(50)             NOT NULL,
    system_url		 varchar(150)            NOT NULL,
    key_value 		 varchar(100)            NOT NULL
);

CREATE TABLE IF NOT EXISTS users.user_auth_key_map (
    user_id         integer                 NOT NULL REFERENCES users.users ON DELETE CASCADE ON UPDATE CASCADE,
    authkey_id      integer                 NOT NULL REFERENCES users.auth_keys ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(authkey_id, user_id)
);

CREATE TABLE IF NOT EXISTS users.project_owners (
    project_id      integer                 NOT NULL REFERENCES project_data.projects ON DELETE CASCADE ON UPDATE CASCADE,
    user_id         integer                 NOT NULL REFERENCES users.users ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY(project_id, user_id)
);

--------------------------------------------------------------------------------
-- Indexes
--