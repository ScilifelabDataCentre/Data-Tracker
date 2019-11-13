--
-- PostgreSQL database dump
--

-- Dumped from database version 10.6 (Debian 10.6-1.pgdg90+1)
-- Dumped by pg_dump version 11.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: data_urls; Type: TABLE DATA; Schema: datasets; Owner: postgres
--

COPY project_data.data_urls (id, url, description) FROM stdin;
1	https:www.example.com/url1	URL description 1
2	https:www.example.com/url2	URL description 2
3	https:www.example.com/url3	URL description 3
4	https:www.example.com/url4	URL description 4
5	https:www.example.com/url5	URL description 5
6	https:www.example.com/url6	URL description 6
7	https:www.example.com/url7	URL description 7
8	https:www.example.com/url8	URL description 8
9	https:www.example.com/url9	URL description 9
10	https:www.example.com/url10	URL description 10
11	https:www.example.com/url11	URL description 11
\.

SELECT pg_catalog.setval('project_data.data_urls_id_seq', 11, true);

--
-- Data for Name: datasets; Type: TABLE DATA; Schema: datasets; Owner: postgres
--

COPY project_data.datasets (id, title, description, doi, creator, dmp) FROM stdin;
1	Dataset title 1	Dataset 1 description	doi.portal.1	A facility 1	dmp url 1
2	Dataset title 2	Dataset 2 description	doi.portal.2	A facility 2	\N
3	Dataset title 3	Dataset 3 description	doi.portal.3	A facility 3	dmp url 3
4	Dataset title 4	Dataset 4 description	doi.portal.4	A facility 4	dmp url 4
5	Dataset title 5	<p>Dataset 5 description; long</p>\n<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce quis risus in nibh efficitur auctor vitae quis magna. Quisque mollis auctor tellus, sed sodales orci. Ut at lectus libero. Aenean eget quam sem. Fusce a eros viverra, consectetur magna nec, commodo dui. Vestibulum rutrum urna a neque bibendum accumsan. Nunc sem mauris, tempor vel congue vitae, venenatis vitae quam. <a href="http://talavis.eu/menu">Ut</a> consectetur nulla sem, eget bibendum ipsum auctor sit amet. Aenean egestas gravida felis, a tempor diam. Vestibulum consequat felis vitae imperdiet convallis. Nam molestie sagittis ante, in rutrum nibh ullamcorper at.</p>\n\n<p>Nam non accumsan tortor, non mattis est. Curabitur vehicula, neque nec iaculis posuere, elit magna laoreet ante, non condimentum libero tellus quis mauris. Ut nec varius orci, non luctus lorem. Morbi ut erat eu leo fringilla faucibus sed ut nulla. Proin ante massa, volutpat ut sapien sit amet, facilisis euismod nunc. Maecenas luctus arcu ac massa vulputate accumsan. Proin ac orci molestie, facilisis elit a, rutrum urna. Suspendisse euismod risus ex, ut efficitur leo molestie vel. Nulla sed metus non justo suscipit pretium sed sit amet mi. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.</p>\n\n<p>Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed urna ipsum, commodo quis neque ac, dignissim lobortis diam. Aenean tempus ut est id maximus. Phasellus ipsum nunc, fringilla et pellentesque non, consectetur eget ipsum. Cras eget tortor vestibulum, tempus nunc luctus, maximus urna. Aenean non fermentum ligula. Donec auctor a nunc a malesuada. Cras semper auctor tellus, at vehicula mauris volutpat vel. Morbi elementum porta vulputate. Quisque et diam eu ligula accumsan vulputate. Fusce rutrum eros et massa gravida, quis ornare augue feugiat. Pellentesque elementum tincidunt enim in placerat. Vestibulum ut dolor gravida, efficitur libero sed, volutpat felis. Duis eget odio consectetur, elementum sem sed, vulputate eros. Fusce pulvinar tortor vel libero volutpat euismod. Donec pharetra justo sed cursus ultrices.</p>\n\n<p>Proin ut elit nec neque maximus varius. Integer sed tortor nunc. Integer imperdiet molestie orci id ornare. Aliquam ultricies augue et ipsum varius mollis. Proin mollis maximus neque, at vestibulum ex porta a. Phasellus nisl neque, semper ac consectetur sit amet, sodales eu sapien. Sed accumsan augue a rhoncus mattis. Aenean elementum mattis tellus sed interdum. Donec viverra nisi magna.</p>	doi.portal.5	A facility 5	\N
6	Dataset title 6	Dataset 6 description	doi.portal.6	A facility 6	\N
\.

SELECT pg_catalog.setval('project_data.datasets_id_seq', 6, true);

COPY project_data.projects (id, title, description, contact) FROM stdin;
1	Project title 1	Project 1 description	Contact@place1
2	Project title 2	Project 2 description	Contact@place2
3	Project title 3	Project 3 description	Contact@place3
4	Project title 4	Project 4 description	Contact@place4
5	Project title 5	Project 5 description	Contact@place5
6	Project title 6	Project 6 description	Contact@place6
\.

SELECT pg_catalog.setval('project_data.projects_id_seq', 6, true);

COPY project_data.project_dataset_map (project_id, dataset_id) FROM stdin;
1	1
1	2
3	3
3	4
4	4
5	6
6	4
\.


--
-- Data for Name: dataset_data_url_map; Type: TABLE DATA; Schema: datasets; Owner: postgres
--

COPY project_data.dataset_data_url_map (dataset_id, data_url_id) FROM stdin;
1	1
1	2
3	3
3	4
4	5
4	6
4	7
5	8
5	9
5	10
6	11
\.

COPY project_data.related_projects (project_id, project_id2, relation_type) FROM stdin;
2	1	PART_OF
3	2	SUPERSEEDED_BY
1	4	DEPENDS_ON
5	6	FOLLOWS
\.


--
-- Data for Name: publications; Type: TABLE DATA; Schema: datasets; Owner: postgres
--

COPY project_data.publications (id, identifier) FROM stdin;
1	A publication1. Journal:2011
2	A publication2. Journal:2012
3	A publication3. Journal:2013
\.

SELECT pg_catalog.setval('project_data.publications_id_seq', 3, true);

--
-- Data for Name: dataset_publication_map; Type: TABLE DATA; Schema: datasets; Owner: postgres
--

COPY project_data.dataset_publication_map (dataset_id, publication_id) FROM stdin;
1	1
3	2
5	3
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: datasets; Owner: postgres
--

COPY project_data.tags (id, title) FROM stdin;
1	Tag Title 1
2	Tag Title 2
3	Tag Title 3
4	Tag Title 4
5	Tag Title 5
6	Tag Title 6
7	Tag Title 7
8	Tag Title 8
9	Tag Title 9
10	Tag Title 10
\.

SELECT pg_catalog.setval('project_data.tags_id_seq', 10, true);


--
-- Data for Name: dataset_tag_map; Type: TABLE DATA; Schema: datasets; Owner: postgres
--

COPY project_data.dataset_tag_map (dataset_id, tag_id) FROM stdin;
1	2
1	3
1	4
1	5
1	8
2	1
2	3
4	5
4	7
5	8
5	1
5	6
6	7
6	9
6	10
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: users; Owner: postgres
--

COPY users.users (id, given_name, email, affiliation, country, auth_identity, permission) FROM stdin;
1	A Name1	user1@example.com	A University1	A Country1	user1auth	Standard
2	A Name2	user2@example.com	A University2	A Country2	user2auth	Standard
3	A Name3	user3@example.com	A University3	A Country3	user3auth	Standard
4	A Name4	user4@example.com	A University4	A Country4	user4auth	Standard
5	A Name5	user5@example.com	A University5	A Country5	user5auth	Steward
6	A Name6	user6@example.com	A University6	A Country6	user6auth	Admin
\.

SELECT pg_catalog.setval('users.users_id_seq', 6, true);
--
-- Data for Name: dataset_owners; Type: TABLE DATA; Schema: users; Owner: postgres
--

COPY users.project_owners (project_id, user_id) FROM stdin;
1	1
1	2
2	2
3	3
3	4
4	4
5	6
6	4
\.



COPY users.auth_keys (id, system_name, system_url, key_value) FROM stdin;
1	http://order1.portal	Order Portal	01234556789ABCDEF
2	http://order2.portal	Order Portal	1234556789ABCDEF0
\.

SELECT pg_catalog.setval('users.auth_keys_id_seq', 2, true);

COPY users.user_auth_key_map (user_id, authkey_id) FROM stdin;
1	1
2	2
\.



