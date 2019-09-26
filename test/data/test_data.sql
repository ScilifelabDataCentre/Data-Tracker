INSERT INTO users.users (given_name, email, affiliation, country, auth_identity, permission) VALUES ('A Name1', 'user1@example.com', 'A University1', 'A Country1', 'user1auth', 'Standard');
INSERT INTO users.users (given_name, email, affiliation, country, auth_identity, permission) VALUES ('A Name2', 'user2@example.com', 'A University2', 'A Country2', 'user2auth', 'Standard');
INSERT INTO users.users (given_name, email, affiliation, country, auth_identity, permission) VALUES ('A Name3', 'user3@example.com', 'A University3', 'A Country3', 'user3auth', 'Standard');
INSERT INTO users.users (given_name, email, affiliation, country, auth_identity, permission) VALUES ('A Name4', 'user4@example.com', 'A University4', 'A Country4', 'user4auth', 'Standard');
INSERT INTO users.users (given_name, email, affiliation, country, auth_identity, permission) VALUES ('A Name5', 'user5@example.com', 'A University5', 'A Country5', 'user5auth', 'Steward');
INSERT INTO users.users (given_name, email, affiliation, country, auth_identity, permission) VALUES ('A Name6', 'user6@example.com', 'A University6', 'A Country6', 'user6auth', 'Admin');

INSERT INTO datasets.datasets (title, description, doi, creator, contact, dmp, visible) VALUES ('Dataset title 1', 'Dataset 1 description', 'doi.portal.1', 'A facility 1', 'contact1@example.com', 'dmp url 1', TRUE);
INSERT INTO datasets.datasets (title, description, doi, creator, contact, dmp, visible) VALUES ('Dataset title 2', 'Dataset 2 description', 'doi.portal.2', 'A facility 2', 'contact2@example.com', Null, TRUE);
INSERT INTO datasets.datasets (title, description, doi, creator, contact, dmp, visible) VALUES ('Dataset title 3', 'Dataset 3 description', 'doi.portal.3', 'A facility 3', 'contact3@example.com', 'dmp url 3', TRUE);
INSERT INTO datasets.datasets (title, description, doi, creator, contact, dmp, visible) VALUES ('Dataset title 4', 'Dataset 4 description', 'doi.portal.4', 'A facility 4', 'contact4@example.com', 'dmp url 4', FALSE);
INSERT INTO datasets.datasets (title, description, doi, creator, contact, dmp, visible) VALUES ('Dataset title 5', 'Dataset 5 description', 'doi.portal.5', 'A facility 5', 'contact5@example.com', Null, FALSE);
INSERT INTO datasets.datasets (title, description, doi, creator, contact, dmp, visible) VALUES ('Dataset title 6', 'Dataset 6 description', 'doi.portal.6', 'A facility 6', 'contact6@example.com', Null, TRUE);

INSERT INTO users.dataset_owners VALUES (1, 1);
INSERT INTO users.dataset_owners VALUES (1, 2);
INSERT INTO users.dataset_owners VALUES (3, 3);
INSERT INTO users.dataset_owners VALUES (3, 4);
INSERT INTO users.dataset_owners VALUES (4, 4);
INSERT INTO users.dataset_owners VALUES (5, 6);
INSERT INTO users.dataset_owners VALUES (6, 4);

INSERT INTO datasets.tags (title) VALUES ('Tag Title 1');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 2');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 3');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 4');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 5');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 6');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 7');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 8');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 9');
INSERT INTO datasets.tags (title) VALUES ('Tag Title 10');

INSERT INTO datasets.dataset_tag_map VALUES (1, 2);
INSERT INTO datasets.dataset_tag_map VALUES (1, 3);
INSERT INTO datasets.dataset_tag_map VALUES (1, 4);
INSERT INTO datasets.dataset_tag_map VALUES (1, 5);
INSERT INTO datasets.dataset_tag_map VALUES (1, 8);
INSERT INTO datasets.dataset_tag_map VALUES (2, 1);
INSERT INTO datasets.dataset_tag_map VALUES (2, 3);
INSERT INTO datasets.dataset_tag_map VALUES (4, 5);
INSERT INTO datasets.dataset_tag_map VALUES (4, 7);
INSERT INTO datasets.dataset_tag_map VALUES (5, 8);
INSERT INTO datasets.dataset_tag_map VALUES (5, 1);
INSERT INTO datasets.dataset_tag_map VALUES (5, 6);
INSERT INTO datasets.dataset_tag_map VALUES (6, 7);
INSERT INTO datasets.dataset_tag_map VALUES (6, 9);
INSERT INTO datasets.dataset_tag_map VALUES (6, 10);

INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url1', 'URL description 1');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url2', 'URL description 2');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url3', 'URL description 3');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url4', 'URL description 4');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url5', 'URL description 5');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url6', 'URL description 6');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url7', 'URL description 7');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url8', 'URL description 8');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url9', 'URL description 9');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url10', 'URL description 10');
INSERT INTO datasets.data_urls (url, description) VALUES ('https:www.example.com/url11', 'URL description 11');

INSERT INTO datasets.dataset_data_url_map VALUES (1,1);
INSERT INTO datasets.dataset_data_url_map VALUES (1,2);
INSERT INTO datasets.dataset_data_url_map VALUES (3,3);
INSERT INTO datasets.dataset_data_url_map VALUES (3,4);
INSERT INTO datasets.dataset_data_url_map VALUES (4,5);
INSERT INTO datasets.dataset_data_url_map VALUES (4,6);
INSERT INTO datasets.dataset_data_url_map VALUES (4,7);
INSERT INTO datasets.dataset_data_url_map VALUES (5,8);
INSERT INTO datasets.dataset_data_url_map VALUES (5,9);
INSERT INTO datasets.dataset_data_url_map VALUES (5,10);
INSERT INTO datasets.dataset_data_url_map VALUES (6,11);

INSERT INTO datasets.publications (identifier) VALUES ('A publication1. Journal:2011');
INSERT INTO datasets.publications (identifier) VALUES ('A publication2. Journal:2012');
INSERT INTO datasets.publications (identifier) VALUES ('A publication3. Journal:2013');

INSERT INTO datasets.dataset_publication_map VALUES (1,1);
INSERT INTO datasets.dataset_publication_map VALUES (3,2);
INSERT INTO datasets.dataset_publication_map VALUES (5,3);
