from pathlib import Path
from pipeline.stage import PipelineStage
from utils.json_helper import JsonHelper

class SqlGen(PipelineStage):
    def validate(self, input_data):
        if not Path(input_data).exists():
            return False
        
        meeting_data = JsonHelper.load_json_data(input_data)
        
        required_keys = ["date", "video_url", "agenda_items", "summaries", "chunk_data"]
        if not all(key in meeting_data for key in required_keys):
            return False
        
        if not isinstance(meeting_data["agenda_items"], dict) or "items" not in meeting_data["agenda_items"]:
            return False
        if not isinstance(meeting_data["agenda_items"]["items"], list):
            return False
        
        if not isinstance(meeting_data["summaries"], list):
            return False

        if not isinstance(meeting_data["chunk_data"], list):
            return False
        
        if not isinstance(meeting_data["date"], str) or len(meeting_data["date"]) == 0:
            return False
        if not isinstance(meeting_data["video_url"], str) or len(meeting_data["video_url"]) == 0:
            return False
        
        return True
    
    def execute(self, intput_data):      
        meeting_data = JsonHelper.load_json_data(intput_data)  

        date, video_url = meeting_data["date"], meeting_data["video_url"]        
        agenda_items, summaries, chunk_data = meeting_data["agenda_items"]["items"], meeting_data["summaries"], meeting_data["chunk_data"]   

         

        sql_text = f"""
        BEGIN;

        -- Insert meeting (ID will auto-generate)
        INSERT INTO public."Meetings" ("Date","VideoURL","Title") VALUES
        ('{date}','{video_url}','City Council Meeting'),

        -- Insert agenda items
        WITH m AS (
            SELECT "MeetingID" AS mid 
            FROM public."Meetings" 
            WHERE "Date" = '{date}'
        )
        INSERT INTO public."AgendaItems" ("MeetingID", "ItemNumber", "FileNumber", "Title", "Description")
        SELECT
            m.mid,
            (j->>'item_number')::int,
            j->>'file_number',
            j->>'title',
            COALESCE(j->>'description', '')
        FROM m,
            jsonb_array_elements('{agenda_items}'::jsonb) AS j;

        -- Insert summaries
        WITH m AS (
            SELECT "MeetingID" AS mid 
            FROM public."Meetings" 
            WHERE "Date" = '{date}'
        )
        INSERT INTO public."Summaries" ("MeetingID","StartTime","Title","Summary")
        SELECT
            m.mid,
            (j->>'StartTime')                     AS StartTime,
            j->>'Title'                           AS Title,
            j->>'Summary'                         AS Summary
        From m,
            jsonb_array_elements('{summaries}'::jsonb) AS j;
        
        -- Insert chunks
        WITH m AS (
            SELECT "MeetingID" AS mid 
            FROM public."Meetings" 
            WHERE "Date" = '{date}'
        )
        INSERT INTO public."Chunks" ("MeetingID", "ChunkNum", "StartTime", "EndTime", "Content", "Embedding")
        SELECT
            m.mid,
            (j->>'ChunkNum')::integer,
            (j->>'StartTime')::float,
            (j->>'EndTime')::float,
            j->>'Content',
            (j->>'Embedding')::vector
        FROM m,
            jsonb_array_elements('{chunk_data}'::jsonb) AS j;
            COMMIT;
        """

        output_path = str(Path(self.config.output_dir / f"Meeting_{date}.sql"))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(sql_text)

        return output_path
    
    def cleanup(self):
        pass