import os
from pathlib import Path
from utils.json_helper import JsonHelper
from pipeline.stage import PipelineStage
from utils.meeting_summary import MeetingSummary
from utils.embed_helper import EmbedHelper

class ChunkGen(PipelineStage):
    def validate(self, input_data):
        transcript_file = None
        if isinstance(input_data, dict):
            transcript_file = input_data.get("transcript_file")
        elif isinstance(input_data, str):
            transcript_file = input_data
        else:
            self.logger.error(f"input_data must be a file path string or dict, got {type(input_data)}")
            return False

        if not isinstance(transcript_file, str):
            self.logger.error("Missing or invalid 'transcript_file'")
            return False

        if not transcript_file.endswith('.json'):
            self.logger.error(f"transcript_file must be a .json file, got: {transcript_file}")
            return False

        if not os.path.isfile(transcript_file):
            self.logger.error(f"File does not exist: {transcript_file}")
            return False

        data = JsonHelper.load_json_data(transcript_file)
        if data is None:
            self.logger.error(f"Failed to load JSON from: {transcript_file}")
            return False

        if not isinstance(data, dict):
            self.logger.error(f"JSON root must be an dict, got {type(data)}")
            return False

        if len(data) == 0:
            self.logger.error("JSON object is empty")
            return False

        segments = data.get("segments")
        if not isinstance(segments, list) or len(segments) == 0:
            self.logger.error("JSON must contain a non-empty 'segments' list")
            return False

        return True
    
    def execute(self, input_data):
        transcript_file = input_data.get("transcript_file") if isinstance(input_data, dict) else input_data
        options = input_data.get("options", {}) if isinstance(input_data, dict) else {}

        meeting_sum = MeetingSummary(meeting_json_path=transcript_file,
                                     chunk_sum_model=MeetingSummary.summary_models["llama-8b"],
                                     fin_select_model=MeetingSummary.summary_models["llama-8b"],
                                     emb_model=MeetingSummary.embedding_models["qwen-4b"])

        meeting_sum.chunk_opts = {
            'method': 'semantic',
            'delim': '\n',
            'lines_per_chunk': options.get("lines_per_chunk", 50),
            'overlap': options.get("overlap", 5),
        }

        chunk_records = meeting_sum.get_chunk_records()
        if len(chunk_records) == 0:
            raise ValueError("No chunks were generated from transcript")

        chunks = [record["chunk"] for record in chunk_records]

        embedder = EmbedHelper(embedding_model=meeting_sum.cur_emb_model)
        vectors = embedder.embed_list(str_list=chunks)

        if len(vectors) != len(chunk_records):
            raise ValueError(f"Embedding count mismatch: {len(vectors)} vectors for {len(chunk_records)} chunks")

        chunks_embeddings = []
        for record, vector in zip(chunk_records, vectors):
            chunks_embeddings.append({
                "chunknum": record["chunknum"],
                "starttime": record["starttime"],
                "endtime": record["endtime"],
                "chunk": record["chunk"],
                "embedding": vector,
            })

        output_file = Path(transcript_file)
        artifact_name = output_file.stem + "_chunks_embeddings.json"
        artifact_path = output_file.parent / artifact_name

        artifact = {
            "transcript_file": transcript_file,
            "chunk_opts": meeting_sum.chunk_opts,
            "embedding_model": meeting_sum.cur_emb_model,
            "chunks_embeddings": chunks_embeddings,
            "chunks": chunks,
            "embeddings": vectors,
        }

        JsonHelper.write_json_data(str(artifact_path), artifact)
        return str(artifact_path)
    
    def cleanup(self):
        pass