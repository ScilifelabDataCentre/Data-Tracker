CREATE SCHEMA IF NOT EXISTS datasets;

CREATE TABLE IF NOT EXISTS datasets.datasets (
    id integer PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    title           varchar(100)            NOT NULL,
    description     text                    DEFAULT NULL,
    doi             varchar(60)             DEFAULT NULL,
    creator         varchar(50)             DEFAULT NULL,
    contact         varchar(100)            DEFAULT NULL,
    dmp             varchar(100)            DEFAULT NULL,
    visible         boolean                 NOT NULL
);

CREATE TABLE IF NOT EXISTS datasets.publications (
    id              integer                 PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    identifier      text                    NOT NULL
);

CREATE TABLE IF NOT EXISTS datasets.dataset_publication_map (
    dataset_id      integer                 NOT NULL REFERENCES datasets.datasets,
    publication_id  integer                 NOT NULL REFERENCES datasets.publications,
    PRIMARY KEY(dataset_id, publication_id)
);

CREATE TABLE IF NOT EXISTS datasets.tags (
    id              integer                 PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    title           varchar(100)            NOT NULL
);

CREATE TABLE IF NOT EXISTS datasets.dataset_tag_map (
    dataset_id      integer                 NOT NULL REFERENCES datasets.datasets,
    tag_id          integer                 NOT NULL REFERENCES datasets.tags,
    PRIMARY KEY(dataset_id, tag_id)
);

CREATE TABLE IF NOT EXISTS datasets.data_urls (
    id integer PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    url             varchar(200)            DEFAULT NULL,
    description     varchar(100)            DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS datasets.dataset_data_url_map (
    dataset_id      integer                 NOT NULL REFERENCES datasets.datasets,
    data_url_id     integer                 NOT NULL REFERENCES datasets.data_urls,
    PRIMARY KEY(dataset_id, data_url_id)
);


--------------------------------------------------------------------------------
-- Indexes
--
