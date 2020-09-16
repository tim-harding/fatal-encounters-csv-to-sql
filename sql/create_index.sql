CREATE INDEX index_{}_name_btree
    ON public.{} USING btree
    (name text_pattern_ops ASC NULLS LAST)
    TABLESPACE pg_default;

CREATE INDEX index_{}_name_gin
    ON public.{} USING gin
    (name gin_trgm_ops)
    TABLESPACE pg_default;