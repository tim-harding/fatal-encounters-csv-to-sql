CREATE TABLE public.incident
(
    id integer NOT NULL,
    name text,
    age integer,
    is_male boolean,
    race integer NOT NULL,
    race_with_imputations integer NOT NULL,
    imputation_probability real,
    image_url text,
    date date NOT NULL,
    address text,
    city integer,
    zipcode integer,
    county integer NOT NULL,
    latitude real NOT NULL,
    longitude real NOT NULL,
    agency integer NOT NULL,
    cause integer NOT NULL,
    description text,
    use_of_force integer NOT NULL,
    article_url text,
    video_url text,
    CONSTRAINT incident_pkey PRIMARY KEY (id)
);