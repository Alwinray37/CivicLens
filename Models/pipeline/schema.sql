BEGIN;
CREATE EXTENSION IF NOT EXISTS vector;

-- ========== DROP FUNCTIONS ==========
DROP FUNCTION IF EXISTS public.get_meeting_json(integer) CASCADE;
DROP FUNCTION IF EXISTS public.insert_meeting(date, text, text) CASCADE;
DROP FUNCTION IF EXISTS public.insert_meeting_embedding(integer, integer, float, float, text, vector) CASCADE;
DROP FUNCTION IF EXISTS public.insert_summary(integer, text, text, text) CASCADE;
DROP FUNCTION IF EXISTS public.attach_document(integer, text, bytea) CASCADE;
DROP FUNCTION IF EXISTS public.ensure_document_type(text) CASCADE;
DROP FUNCTION IF EXISTS public.add_agenda_item(integer, text, text, integer, text, integer) CASCADE;
DROP FUNCTION IF EXISTS public.get_meetings_json() CASCADE;

-- ========== DROP TABLES ==========
DROP TABLE IF EXISTS public."Documents" CASCADE;
DROP TABLE IF EXISTS public."DocumentDatas" CASCADE;
DROP TABLE IF EXISTS public."DocumentTypes" CASCADE;
DROP TABLE IF EXISTS public."AgendaItems" CASCADE;
DROP TABLE IF EXISTS public."Summaries" CASCADE;
DROP TABLE IF EXISTS public."Meetings" CASCADE;
DROP TABLE IF EXISTS public."MeetingChunks" CASCADE;

-- ========== TABLES ==========

CREATE TABLE public."Meetings" (
    "MeetingID" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "Date" date NOT NULL,
    "VideoURL" text NOT NULL,
    "Title" text NOT NULL
);

CREATE TABLE public."MeetingChunks" (
    "ChunkID" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "meeting_id" integer NOT NULL REFERENCES public."Meetings"("MeetingID") ON UPDATE CASCADE ON DELETE CASCADE,
    -- needs to be lowercase for pgvectorstore compatibility
    "ChunkNum" integer NOT NULL,
    "StartTime" float NOT NULL,
    "EndTime" float NOT NULL,
    "Content" text NOT NULL,
    "Embedding" vector(2560) NOT NULL
);

CREATE TABLE public."AgendaItems" (
    "AgendaItemID" bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "MeetingID" integer NOT NULL REFERENCES public."Meetings"("MeetingID") ON UPDATE CASCADE ON DELETE CASCADE,
    "Title" text NOT NULL,
    "Description" text NOT NULL,
    "ItemNumber" integer NOT NULL,
    "OrderNumber" integer NOT NULL,
    "FileNumber" text
);

CREATE TABLE public."Summaries" (
    "SummaryId" bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "MeetingID" integer NOT NULL REFERENCES public."Meetings"("MeetingID") ON UPDATE CASCADE ON DELETE CASCADE,
    "Title" text NOT NULL,
    "Summary" text NOT NULL,
    "StartTime" text NOT NULL
);

CREATE TABLE public."DocumentTypes" (
    "DocumentTypeID" smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "Name" text NOT NULL UNIQUE
);

CREATE TABLE public."DocumentDatas" (
    "DocumentDataID" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "DocumentTypeID" smallint NOT NULL REFERENCES public."DocumentTypes"("DocumentTypeID") ON UPDATE CASCADE ON DELETE CASCADE,
    "Data" bytea NOT NULL
);

CREATE TABLE public."Documents" (
    "DocumentID" integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    "MeetingID" integer NOT NULL REFERENCES public."Meetings"("MeetingID") ON UPDATE CASCADE ON DELETE CASCADE,
    "DocumentDataID" integer NOT NULL REFERENCES public."DocumentDatas"("DocumentDataID") ON UPDATE CASCADE ON DELETE CASCADE
);

-- ========== FUNCTIONS ==========

CREATE FUNCTION public.ensure_document_type(p_name text) RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE id int;
BEGIN
  INSERT INTO "DocumentTypes"("Name") VALUES (p_name)
  ON CONFLICT ("Name") DO NOTHING;
  SELECT "DocumentTypeID" INTO id FROM "DocumentTypes" WHERE "Name" = p_name;
  RETURN id;
END$$;

COMMENT ON FUNCTION public.ensure_document_type(p_name text)
IS 'Upsert by name; return id';

CREATE FUNCTION public.add_agenda_item(
  p_meeting_id integer,
  p_title text,
  p_description text,
  p_item_number integer,
  p_file_number text,
  p_order integer
) RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE new_id bigint; v_order int;
BEGIN
  v_order := COALESCE(
    p_order,
    (SELECT COALESCE(MAX("OrderNumber"), 0) + 1
     FROM "AgendaItems"
     WHERE "MeetingID" = p_meeting_id)
  );

  INSERT INTO "AgendaItems"(
    "MeetingID", "Title", "Description", "ItemNumber", "OrderNumber", "FileNumber"
  )
  VALUES (
    p_meeting_id, p_title, p_description, p_item_number, v_order, p_file_number
  )
  RETURNING "AgendaItemID" INTO new_id;

  RETURN new_id;
END$$;

CREATE FUNCTION public.attach_document(p_meeting_id integer, p_document_type_name text, p_data bytea)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE type_id int; data_id int; doc_id int;
BEGIN
  type_id := ensure_document_type(p_document_type_name);

  INSERT INTO "DocumentDatas"("DocumentTypeID","Data")
  VALUES (type_id, p_data)
  RETURNING "DocumentDataID" INTO data_id;

  INSERT INTO "Documents"("MeetingID","DocumentDataID")
  VALUES (p_meeting_id, data_id)
  RETURNING "DocumentID" INTO doc_id;

  RETURN doc_id;
END$$;

CREATE FUNCTION public.insert_meeting(p_date date, p_videourl text, p_title text)
RETURNS integer
LANGUAGE plpgsql
AS $$
DECLARE new_id integer;
BEGIN
  INSERT INTO "Meetings" ("Date", "VideoURL", "Title")
  VALUES (p_date, p_videourl, p_title)
  RETURNING "MeetingID" INTO new_id;
  RETURN new_id;
END;$$;

CREATE FUNCTION public.insert_summary(
  p_meeting_id integer,
  p_title text,
  p_summary text,
  p_start_time text
)
RETURNS bigint
LANGUAGE plpgsql
AS $$
DECLARE new_id bigint;
BEGIN
  INSERT INTO "Summaries" ("MeetingID", "Title", "Summary", "StartTime")
  VALUES (p_meeting_id, p_title, p_summary, p_start_time)
  RETURNING "SummaryId" INTO new_id;
  RETURN new_id;
END;$$;

CREATE FUNCTION public.insert_meeting_embedding(
  p_meeting_id integer,
  p_chunk_num integer,
  p_start_time float,
  p_end_time float,
  p_content text,
  p_embedding vector
)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO "MeetingChunks" ("meeting_id", "ChunkNum", "StartTime", "EndTime", "Content", "Embedding")
  VALUES (p_meeting_id, p_chunk_num, p_start_time, p_end_time, p_content, p_embedding);
END;$$;

CREATE FUNCTION public.get_meetings_json()
RETURNS jsonb
LANGUAGE sql
STABLE
AS $$
SELECT jsonb_agg(to_jsonb(m) ORDER BY m."Date" DESC, m."MeetingID" DESC)
FROM public."Meetings" m;
$$;

CREATE FUNCTION public.get_meeting_json(p_meeting_id integer)
RETURNS jsonb
LANGUAGE sql
AS $$
SELECT jsonb_build_object(
  'meeting', to_jsonb(m),
  'agenda', (SELECT jsonb_agg(to_jsonb(a) ORDER BY "OrderNumber")
             FROM "AgendaItems" a WHERE a."MeetingID" = m."MeetingID"),
  'summaries', (SELECT jsonb_agg(to_jsonb(s))
             FROM "Summaries" s WHERE s."MeetingID" = m."MeetingID"),
  'documents', (
    SELECT jsonb_agg(jsonb_build_object(
      'documentId', d."DocumentID",
      'dataId', dd."DocumentDataID",
      'type', dt."Name"
    ))
    FROM "Documents" d
    JOIN "DocumentDatas" dd ON dd."DocumentDataID" = d."DocumentDataID"
    JOIN "DocumentTypes" dt ON dt."DocumentTypeID" = dd."DocumentTypeID"
    WHERE d."MeetingID" = m."MeetingID")
)
FROM "Meetings" m WHERE m."MeetingID" = p_meeting_id;
$$;

COMMIT;
