CREATE TABLE USERS (
    id integer PRIMARY KEY,
    first_name text NOT NULL,
    joined_on timestamptz NULL DEFAULT CURRENT_TIMESTAMP(0)
);

CREATE TABLE URLS (
    id SERIAL PRIMARY KEY,
    owner integer CONSTRAINT owner_must_exist REFERENCES USERS ON DELETE CASCADE,
    url text NOT NULL CONSTRAINT must_be_lowercase CHECK (url = lower(url)),
    title text NULL,
    CONSTRAINT only_unique_urls_per_user UNIQUE (owner, url)
);