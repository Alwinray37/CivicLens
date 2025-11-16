import json
from ollama import chat
from ollama import ChatResponse

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
    @staticmethod
    def get_per_chunk_prompt(chunk):
        """
        Creates a prompt to be used when summarizing 
        individual transcript chunks
    
        Parameters:
            chunk (str): The chunk to be summarized
    
        Returns:
            str: The created prompt
        """
        
        return f"""
You will receive a chunk of an SRT transcript.

Each SRT entry has this format:
[index number]
[start_time --> end_time]
[text]

Your task:
1. Read all start times in the chunk. A start time is the first time in any line with the pattern "HH:MM:SS,MMM -->".
2. Use the earliest start time that actually appears.
3. Do not guess or invent any times.
4. Create:
    - A short, descriptive title based ONLY on the content of the chunk.
    - The title must NOT include words like: SRT, transcript, chunk, file, section, or similar meta words.
    - The title should describe what the people are talking about.
    - A 3–5 sentence summary of the discussion.

Output ONLY in this format:

StartTime: [start_time]
Title: [title]
Summary: [summary]

Here is the chunk:
{chunk}
""".strip()

    
    @staticmethod
    def get_important_events_prompt(summaries):
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
{"\n".join(summaries)}
""".strip()
    
    @staticmethod
    def chunk_transcript_file(file_path, encoding='utf-8', lines_per_chunk=10):
        """
        Creates chunks at a given interval of a transcript at a given
        path
    
        Parameters:
            file_path (str): The path of the SRT transcript file
            encoding (str): The encoding to use when reading the file
            lines_per_chunk (int): The amount of transcript lines you want per chunk
    
        Returns:
            list[str]: A list of the created chunks
        """
        with open(file_path, 'r', encoding=encoding) as file:
            file_content = file.read()
    
            i = 0
            c_id = 0
            lines = file_content.split('\n\n')
    
            chunks = []
            while i < len(lines):
                chunk = lines[i:i+lines_per_chunk]
                chunk_str = "\n\n".join(chunk)
                chunks.append(chunk_str)
                i += lines_per_chunk
                c_id += 1
            print(f'Created {c_id} chunks')
            return chunks
            
    
    @staticmethod
    def gen_chunk_summaries(chunks):
        """
        Generates summaries for each of the given chunks from a transcript
    
        Parameters:
            chunks (list[str]): List of chunks to be summarized
    
        Returns:
            list[str]: A list of the created summaries for the chunks
        """
        summaries = []
        for i, chunk in enumerate(chunks):
            prompt = MeetingSummary.get_per_chunk_prompt(chunk=chunk)
            
            ch_response: ChatResponse = chat(model='llama3.2:3b', messages=[
                {
                    'role': 'user',
                    'content': prompt,
                    # 'format': MeetingEvent.model_json_schema(),
                    'options': {
                        'temperature': 0.3,
                    }
                }
            ]
            )
            ch_summ = ch_response['message']['content']
            summaries.append(ch_response['message']['content'])
            print(f'{ch_summ}\n')
            
        # with open('llama3.2_test_summaries.txt', 'w', encoding='utf-8') as file:
        #     file.write("".join(summaries))
        # exit()
        return summaries
        
    @staticmethod
    def important_events_txt_to_json(important_events):
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
                    
    
    
    @staticmethod
    def gen_important_events_from_summaries(summaries):
        """
        Generates a list of important events given a list of summaries
        of chunks from a transcript
        
        Parameters:
            summaries (list[str]): Summaries of chunks from a transcript
    
        Returns:
            list[dict[str, str]]: JSON formatted array
        """
        prompt = MeetingSummary.get_important_events_prompt(summaries=summaries)
        response: ChatResponse = chat(model='llama3.1:8b', messages=[
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
        json_format = MeetingSummary.important_events_txt_to_json(content)
        print(json.dumps(json_format, indent=4))
        
        return json_format
    
    
    @staticmethod
    def gen_important_events_from_srt(srt_path):
        """
        Generates a list of important events given a path to an
        SRT file
        
        Parameters:
            srt_path (str): Path to SRT file
    
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
            
        chunks = MeetingSummary.chunk_transcript_file(file_path=srt_path, lines_per_chunk=50)
        print("Chunked transcript\n")
        summaries = MeetingSummary.gen_chunk_summaries(chunks=chunks)
        print("Summarized chunks\n")
        return MeetingSummary.gen_important_events_from_summaries(summaries=summaries)