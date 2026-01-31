import math
import re
import chromadb
from langchain_community.document_loaders import JSONLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
from ollama import chat
from ollama import ChatResponse
import ollama

import numpy

from sklearn.cluster import KMeans

from chunker import ChunkOpts, Chunker, chunking_method

# If you want to attempt to use the format option with ollama.
# Not currently in use as the models seem to be very iffy when trying to produce consistent JSON.

# from pydantic import BaseModel

# class MeetingEvent(BaseModel):
#     timecode: str
#     title: str
#     summary: str

# class MeetingEvents(BaseModel):
#     events: list[MeetingEvent]

class MeetingSummary:

    embedding_models = {
        "qwen-4b" : "qwen3-embedding:4b"
    }

    summary_models = {
        "llama-3b" : "llama3.2:3b",
        "llama-8b" : "llama3.1:8b",
        "llama-70b" : "llama3.1:70b-instruct-q4_0",
        "gpt-20b" : "gpt-oss:20b"
    }

    cur_chunk_sum_model = summary_models["llama-3b"]
    cur_select_model = summary_models["llama-70b"]
    cur_emb_model = embedding_models["qwen-4b"]    

    chunk_opts: ChunkOpts = {
            'method': 'semantic',
        }

    def __init__(self, meeting_json_path:str, chunk_sum_model: str = summary_models["llama-3b"], fin_select_model: str = summary_models["llama-70b"], emb_model: str = embedding_models["qwen-4b"]):
        loader = JSONLoader(
                file_path=meeting_json_path,
                jq_schema=".segments[]",
                content_key="text",
                metadata_func=self._meeting_metadata_func)

        self.docs = loader.load()
        self.text = ""
        for i, doc in enumerate(self.docs):
            self.text += f"|{i}|: "
            self.text += doc.page_content
            self.text += "\n"

        self.client = chromadb.Client()
        self.client.create_collection(name="chunks")
        self.cur_select_model = chunk_sum_model
        self.cur_select_model = fin_select_model
        self.cur_emb_model = emb_model

        self.chunker = Chunker(emb_model=emb_model)
        self.meeting_chunk_key = str(hash(self.text))

    def _meeting_metadata_func(self, record: dict, metadata: dict) -> dict:
        metadata["start"] = record.get("start") or 0
        metadata["end"] = record.get("end") or 0
        metadata["speaker"] = record.get("speaker") or ""

        return metadata

    def get_meeting_asr_segmented_prompt(self, agenda_json, chunk):
        return f"""
Segment this SRT chunk according to the City Council agenda.

You are given:
- Agenda JSON (list of items with item_number + title + description).
- Minutes text (optional supporting context).
- One SRT CHUNK (several consecutive lines).

Your task:
- Group consecutive SRT lines into meaningful segments.
- For each segment, decide if it matches an agenda item.
- If yes → use the EXACT agenda item title + item_number.
- If no → title = "Not on Agenda", agenda_item_id = null.
- Always choose one classification: "agenda_item", "public_comment", "procedural", or "other".

Your output MUST be exactly one JSON object:

{{
  "segments": [
    {{
      "segment_id": "seg_001",
      "title": "...",
      "agenda_item_id": "... or null",
      "classification": "...",
      "start_time": "HH:MM:SS,mmm",
      "end_time": "HH:MM:SS,mmm",
      "srt_indices": [ ... ],
      "text": "...",
      "reason": "1–2 sentences"
    }}
  ]
}}

Rules:
- Top-level must be an object with only the key "segments".
- No arrays at the top level.
- Use exact start/end times based on included SRT lines.
- Use “Not on Agenda” unless the match is absolutely clear.
- Pre-meeting videos, PSAs, library/college workshop clips → always “other”.

AGENDA JSON:
{agenda_json}

SRT CHUNK:
{chunk}

Produce ONLY the JSON object.
""".strip()

    def get_per_chunk_prompt(self, chunk):
        """
        Creates a prompt to be used when summarizing 
        individual transcript chunks
    
        Parameters:
            chunk (str): The chunk to be summarized
    
        Returns:
            str: The created prompt
        """
        
        return f"""
You are a summarization engine.

You will be given a chunk of dialogue from a civic meeting.
Each line is formatted as:
|{{INDEX}}|: {{SPEECH}}

Your task is to generate:
1. A short, descriptive title for the discussion
2. A concise, neutral summary of the discussion

Rules:
- Output MUST follow this exact format:
  Title: {{GEN_TITLE}}
  Summary: {{GEN_SUM}}
- Output ONLY the title and summary in the specified format.
- Do NOT include introductions, explanations, or extra text.
- Do NOT mention indexes, transcripts, or dialogue structure.
- Do NOT quote speakers directly.
- Do NOT use bullet points, markdown, or headings beyond the required labels.
- Title should be brief (3–8 words) and topic-focused.
- Summary should be written in plain sentences, third person, and neutral in tone.
- If the dialogue is procedural or low-information, generate a general but accurate title and summary.

Dialogue:
{chunk}


Output:
""".strip()

    def get_important_events_prompt(self, summaries):
        
        newline = '\n'
        """
        Creates a prompt to be used when picking the most
        important event out of a list of summaries
    
        Parameters:
            summaries (str): The chunk summaries from a transcript
    
        Returns:
            str: The created prompt
        """
        
        return f"""
You are given a list of processed chunks from a city council meeting.

Each chunk has this format:
StartTime: [time]
Title: [title]
Summary: [summary]

Your task:
Select up to 10 chunks that are the most important based on:
- Civic issues (zoning, housing, budgeting, infrastructure, safety, etc.)
- Policy debates or decisions
- Motions, amendments, proposals, or votes

Ignore chunks that are procedural, greetings, or off-topic unless they contain substantive policy content.

OUTPUT RULES (important):
- Do NOT use bold, italics, or any Markdown formatting.
- Do NOT add numbering, bullets, or commentary.
- Output plain text only.
- Each selected chunk must appear in exactly this format:

StartTime: [time]
Title: [title]
Summary: [summary]

- Separate each chunk with a blank line.
- Do NOT change any text inside the chunks.

Here are the chunks:
[PASTE CHUNKS HERE]
{newline.join(summaries)}
""".strip()

    
    def _seconds_to_srt_str(self, seconds: float) -> str:
        hours = math.floor(seconds / 3600)
        seconds -= hours * 3600
        minutes = math.floor(seconds / 60)
        seconds -= minutes * 60
        
        seconds_rd = math.floor(seconds)
        seconds -= seconds_rd

        ms = int(seconds * 1000)
        
        return f"{hours:0>2d}:{minutes:0>2d}:{seconds_rd:0>2d},{ms:0>3d}"
        
    
    def embed_list(self, str_list: list[str]):
        embeddings = ollama.embed(
            model=MeetingSummary.cur_emb_model,
            input=str_list
        )
        
        return embeddings['embeddings']
        
    
    def embed_and_cluster_chunks(self, chunks: list[str], n_clusters=7):
        vectors = self.embed_list(str_list=chunks)
        clusters = KMeans(n_clusters=n_clusters, random_state=101).fit(vectors)
        print(f'Clustered chunks:\n{clusters.labels_}')
        return (vectors, clusters)
        
    
    
    def get_clustered_chunk_groups(self, chunks: list[str], embeddings=None, n_clusters=7):
        vectors = None
        clusters = None
        
        if embeddings is None:
            vectors, clusters = self.embed_and_cluster_chunks(chunks=chunks, n_clusters=n_clusters)
        else:
            vectors = embeddings
            clusters = KMeans(n_clusters=n_clusters, random_state=101).fit(vectors)
            
        if clusters.labels_ is None:
            return {}
            
        grouped_chunks = {}
        for i, label in enumerate(clusters.labels_):
            if label in grouped_chunks:
                grouped_chunks[label].append({
                    'chunk': chunks[i],
                    'embedding': vectors[i]
                })
            else:
                grouped_chunks[label] = [
                    {
                        'chunk': chunks[i],
                        'embedding': vectors[i]
                    }
                ]
        
        return grouped_chunks
        
        
    
    def get_queried_chunks(self, chunks: list[str]|None=None, ch_embeddings=None, filter_list: list[str]|None=None, fi_embeddings=None, max_query: int = 12):
        collection = self.client.get_collection("chunks")
        
        chunk_embeddings = ch_embeddings or self.embed_list(str_list=chunks or [])
        chunk_embeddings_ids = [str(index) for index, _ in enumerate(chunk_embeddings)]
        
        
        collection.add(
            ids=chunk_embeddings_ids,
            embeddings=chunk_embeddings,
            documents=chunks
        )
        
        filter_embeddings = fi_embeddings or self.embed_list(str_list=filter_list or [])
        
        query_res = collection.query(
            query_embeddings=filter_embeddings,
            n_results=max_query
        )
        
        documents = query_res['documents']
        if documents is not None:
            for i, document in enumerate(documents):
                print(f'Filter {i} queried {len(document)} chunks\n')
        
        return documents or []
    
    def get_centroid_chunks(self, chunks: list[str], n_clusters=7):
        vectors, clusters = self.embed_and_cluster_chunks(chunks=chunks, n_clusters=n_clusters)
        
        closest_list = []
        for i in range(n_clusters):
            dist = numpy.linalg.norm(vectors - clusters.cluster_centers_[i], axis=1)
            closest = numpy.argmin(dist)
            closest_list.append(closest)
            
        centroid_chunks = []
        for index in closest_list:
            centroid_chunks.append(chunks[index])
                
        return centroid_chunks
    
    def gen_chunks_summaries(self, chunks):
        """
        Generates summaries for each of the given chunks from a transcript
    
        Parameters:
            chunks (list[str]): List of chunks to be summarized
    
        Returns:
            list[str]: A list of the created summaries for the chunks
        """
        summaries = []
        for _, chunk in enumerate(chunks):
            first_index_str = re.search(r"(?<=\|)\d+(?=\|)", chunk)
            if first_index_str is None:
                continue
            
            try:
                start_time = self.docs[int(first_index_str.group())].metadata["start"]
            except:
                continue
            

            prompt = self.get_per_chunk_prompt(chunk=chunk)
            
            ch_response: ChatResponse = chat(model=self.cur_chunk_sum_model, messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    # 'format': MeetingEvent.model_json_schema(),
                    'options': {
                        'temperature': 0,
                    }
                }
            ]
            )
            ch_summ = f"StartTime: {start_time}\n{ch_response['message']['content']}"
            summaries.append(ch_summ)
            print(f'{ch_summ}\n')
            
        # with open('llama3.2_test_summaries.txt', 'w', encoding='utf-8') as file:
        #     file.write("".join(summaries))
        # exit()
        return summaries
        
    def important_events_txt_to_json(self, important_events):
        """
        Converts the important events model text output to a
        JSON formatted array
    
        Parameters:
            important_events (str): Important events string generated by model
    
        Returns:
            list[dict[str, str]]: JSON formatted array
        """
        splt_events = important_events.split('\n\n')
        events_json = []
        
        for event in splt_events:
            key_values = event.split("\n")
            event_obj = {}
            for i, pair in enumerate(key_values):
                value = pair.split(": ")[1]
                if i == 0:
                    event_obj['StartTime'] = value
                elif i == 1:
                    event_obj['Title'] = value
                elif i == 2:
                    event_obj['Summary'] = value
            
            events_json.append(event_obj)
        
        return events_json                
    
    def gen_important_events_from_summaries(self, summaries):
        """
        Generates a list of important events given a list of summaries
        of chunks from a transcript
        
        Parameters:
            summaries (list[str]): Summaries of chunks from a transcript
    
        Returns:
            list[dict[str, str]]: JSON formatted array
        """
        prompt = self.get_important_events_prompt(summaries=summaries)
        response: ChatResponse = chat(model=self.cur_select_model, messages=[
        {
            'role': 'user',
            'content': prompt,
            # 'think': True,
            'options': {
                'temperature': 0,
            }
        },
        ])
        
        content = response['message']['content']
        
        # print("---THINKING---\n")
        # print(response['message']['thinking'])
        print("Picked important events\n")
        print(content)
        json_format = self.important_events_txt_to_json(content)
        
        return json_format
    
    
    def gen_important_events(self, lines_per_chunk:int = 50):
        """
        Generates a list of important events using the instance's transcript
    
        Returns:
            list[dict[str, str]]: JSON formatted array
        """
        
        # Current method is very simplistic
            # Chunk a transcript srt file
            # Generate summaries for those chunks
            # Pick most important summaries
        
        # Not currently using agenda items in prompt
        # Model might be too small to consider it
        
        # agenda_file_path = "Agenda_12_Items.json"
        
        # agenda = ''
        # with open(agenda_file_path, 'r', encoding='utf-8') as file:
        #     file_content = file.read()
        #     agenda += file_content
            
        chunks = self.chunker.chunk(text=self.text, key=self.meeting_chunk_key, opts=self.chunk_opts)
        print("Chunked transcript\n")
        summaries = self.gen_chunks_summaries(chunks=chunks)
        print("Summarized chunks\n")
        return self.gen_important_events_from_summaries(summaries=summaries)        
    
    def gen_meeting_asr_segmentation(self, json_agenda, json_minutes, lines_per_chunk=30):
        all_segments = []
       
        chunks = self.chunker.chunk(text=self.text, key=self.meeting_chunk_key, opts=self.chunk_opts)
        
        for chunk_idx, chunk in enumerate(chunks):
            print(f"processing chunk {chunk_idx + 1}/{len(chunks)}")

            prompt = self.get_meeting_asr_segmented_prompt(agenda_json=json_agenda, chunk=chunk)

            response: ChatResponse = chat(
                model = self.cur_select_model,
                messages = [
                    {
                        "role": "user",
                        "content": prompt,                    
                    }
                ],
                options={
                    "temperature": 0,
                },
            )
            raw_response = response["message"]["content"]

            print(raw_response)

            import json
            try:
                segment_data = json.loads(raw_response)
                all_segments.append(segment_data.get("segments", []))
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON for chunk {chunk_idx}: {e}")
                print(f"Raw response was: {raw_response}")

        return all_segments

    def gen_important_events_by_query(self, filter_list: list[str], lines_per_chunk=30, max_query=5):
        chunks = self.chunker.chunk(text=self.text, key=self.meeting_chunk_key, opts=self.chunk_opts)
        # query 5 chunks per filter
        query_res = self.get_queried_chunks(chunks=chunks, filter_list=filter_list, max_query=max_query)
        np_res_arr = numpy.array(query_res)
        
        # flatten and remove duplicates
        queried_chunks = set(np_res_arr.flatten())
        summaries = self.gen_chunks_summaries(chunks=queried_chunks)
        
        return self.gen_important_events_from_summaries(summaries=summaries)
        
        
    def gen_important_events_by_double_query(self, filter_list: list[str], init_lines_per_chunk=100, last_lines_per_chunk=25):
        chunks = self.chunker.chunk(text=self.text, key=self.meeting_chunk_key, opts=self.chunk_opts)
        
        max_query = math.ceil(len(filter_list) / 2)
        
        # query_res comes back as an list of lists of query results based on filter_list length
        query_res = self.get_queried_chunks(chunks=chunks, filter_list=filter_list, max_query=max_query)
        np_res_arr = numpy.array(query_res)
        
        # flatten and remove duplicates
        queried_chunks = set(np_res_arr.flatten())
        
        double_filtered_chunks = []
        for q_chunk in queried_chunks:
            # break down queried chunks into smaller chunks
            small_chunks = self.chunker.chunk(text=q_chunk, key=str(hash(q_chunk)), opts=self.chunk_opts)
            
            # query these smaller chunks
            max_small_query = math.ceil(len(small_chunks) / 2)
            
            q_small_res = self.get_queried_chunks(chunks=small_chunks, filter_list=filter_list, max_query=max_small_query)
            np_res_arr = numpy.array(q_small_res)
            q_small_chunks = set(np_res_arr.flatten())
            
            double_filtered_chunks.extend(q_small_chunks)
        
        print(f'DOUBLE FILTERED CHUNK LEN: {len(double_filtered_chunks)}\n\n')
        summaries = self.gen_chunks_summaries(chunks=set(double_filtered_chunks))
        return self.gen_important_events_from_summaries(summaries=summaries)
    
    
    def get_important_events_by_cluster_centroids(self, lines_per_chunk=30, n_clusters=12):
        chunks = self.chunker.chunk(text=self.text, key=self.meeting_chunk_key, opts=self.chunk_opts)
        
        centroid_chunks = self.get_centroid_chunks(chunks=chunks, n_clusters=n_clusters)
        summaries = self.gen_chunks_summaries(chunks=centroid_chunks)
        return self.gen_important_events_from_summaries(summaries=summaries)
