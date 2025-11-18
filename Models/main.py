import re
import pymupdf
import torch
import torchaudio
import ffmpeg

from json_helper import JsonHelper
from asr_extraction import AsrExtraction

import numpy as np

from dotenv import load_dotenv
import os

from pyannote.audio import Pipeline, Audio
from pyannote.core import Segment
from pyannote.audio.pipelines.utils.hook import ProgressHook

from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline

from huggingface_hub import login

from tqdm import tqdm

from meeting_summary import MeetingSummary

JSON_INFO = 'info.json'
JSON_RAW_OUTPUT = 'output.json'
JSON_MODIFIED_OUTPUT = 'modifiedOutput.json'
JSON_SUMMARY_OUTPUT = 'summary.json'
JSON_SPEAKER_TIME = 'speaker_time.json'
JSON_SPEAKER_WORDS = 'speaker_words.json'
JSON_PDF_EXTRACTION = 'pdf_extraction.json'

def extract_pdf_text(pdf_filname):
    extracted_text = []

    with pymupdf.open(pdf_filname) as doc:
        for page_num, page in enumerate(doc):
            text = page.get_text()
           
            extracted_text.append({
                "page": page_num + 1,
                "text": text.strip()
            })

    return extracted_text

def extract_pdf_raw_text(pdf_filename):
    parts = []
    with pymupdf.open(pdf_filename) as doc:
        for page in doc:
            parts.append(page.get_text())
    return "\n".join(parts)

def extract_agenda_items(pdf_text):
    pattern = re.compile(
        r"\((\d+)\)\s*"                       
        r"(\d{2}-\d{4}(?:-S\d+)?)\s*"        
        r"(?:CD\s*\d+)?\s*"                 
        r"(.+?)(?=\n\(\d+\)\s|$)",           
        re.DOTALL
    )

    junk_line = re.compile(
        r"^(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b"
        r"|^PAGE\b|^- .* -$|^(?:https?://|www\.)",
        re.I
    )

    first_sentence = re.compile(
        r"^(.*?\.)\s*(?=(?:Recommendations?|Fiscal|Community|URGENCY|Items\b|\()|$)",
        re.I | re.DOTALL
    )

    items = []
    for m in pattern.finditer(pdf_text):
        item_no, file_no, block = m.groups()

        block = block.split("\n(", 1)[0]

        lines = [ln.strip() for ln in block.splitlines()
                 if ln.strip() and not junk_line.match(ln.strip())]
        text = re.sub(r"\s+", " ", " ".join(lines)).strip(" -")

        mm = first_sentence.match(text)
        title = (mm.group(1) if mm else text).strip()

        _, _, after_title = text.partition(title)
        after_title = after_title.strip()

        if title:
            items.append({"item_number": item_no, "file_number": file_no, "title": title, "description": after_title})
    return items

def summarize_lines(data):
    summarizer = pipeline(task="summarization", model="sshleifer/distilbart-cnn-12-6")

    """summarization_results = summarizer("PG&E stated it scheduled the blackouts in response to forecasts for high winds "
    "amid dry conditions. The aim is to reduce the risk of wildfires. Nearly 800 thousand customers were "
    "scheduled to be affected by the shutoffs which were expected to last through at least midday tomorrow.", max_length=28)"""

    summarizations = []
    for phrase in tqdm(data, desc="Summary Loop"):

        text = phrase['line']

        summarization_results = summarizer(text)
        
        summarizations.append({"input": phrase['line'], "summary": summarization_results[0]["summary_text"]})        

    return summarizations

def speaker_diarization(audio_filename):
    try:
        diarization_pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization-3.1')
        print("Pipeline loaded successfully")
    except Exception as e:
        print(f"Error loading pipeline: {e}")
        return
    
    if torch.cuda.is_available():
        diarization_pipeline.to(torch.device("cuda"))    

    with ProgressHook() as hook:
        output = diarization_pipeline(audio_filename, hook=hook)
    
    speakers_dict = []
    for turn, _, speaker in output.itertracks(yield_label=True):

        print(f"{speaker} speaks between t={turn.start}s and t={turn.end}s")
        speakers_dict.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })

    return speakers_dict

def combine_words_with_speakers(data, speakers):
    combined = []

    sorted_speakers = sorted(speakers, key=lambda x: x['start'])
    
    curr_word_index = 0
    for i, speaker in enumerate(sorted_speakers):
        s_start = speaker['start']
        s_end = speaker['end']

        speaker_line = ""

        while curr_word_index < len(data):
            word_data = data[curr_word_index]
            word_start = word_data['start']
            word_end = word_data['end']

            speaker_line += word_data['word'] + " "
            curr_word_index += 1

            if not(word_start >= s_start and word_end <= s_end):
                break

        combined.append({
            "speaker": speaker['speaker'],
            "start": s_start,
            "end": s_end,
            "line": speaker_line.strip()
        })

    return combined

def merge_speaker_words(speaker_words):
    merged = {}

    for i, data in enumerate(speaker_words):
        if data['speaker'] not in merged:
            merged[data['speaker']] = {                
                'start': data['start'],
                'end': data['end'],
                'line': data['line']
            }
            continue

        merged[data['speaker']]['line'] += data['line']
        merged[data['speaker']]['end'] = data['end']

    return merged

def get_frame_at_timestamp(input_video, timestamp, output_image):
    try:
        (
            ffmpeg
            .input(input_video, ss=timestamp)
            .filter('crop', 283-60, 273-20, 60, 20) #width, height, x, y
            .output(output_image, vframes=1)
            .run(overwrite_output=True)
        )
        print(f"Frame extracted successfully to {output_image}")
    except ffmpeg.Error as e:
        print(f"Error extracting frame: {e.stderr.decode()}")

def main():
    load_dotenv()

    """Uncomment to login to Huggingface"""
    #pyannote_token = os.getenv("PYANNOTE_TOKEN")
    #login(token=pyannote_token)

    info_data = JsonHelper.load_json_data(JSON_INFO)

    if info_data is None:        
        return
    
    """Uncomment to Run ASR"""    
    #asr_extractor = AsrExtraction()
    #raw_output = asr_extractor.set_raw_output(info_data['Filename'], model_size='small')
    #JsonHelper.write_json_data(raw_output)
    
    """Combine words into time segmented phrases"""
    #raw_output = load_json_data(JSON_RAW_OUTPUT)
    #processed_lines = asr_extractor.combine_words(raw_output, info_data["MaxTime"])
    #write_json_data(JSON_MODIFIED_OUTPUT, processed_lines)

    """BERT Name Entity"""
    """
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    example = "My Alex is Wolfgang and I live in Berlin"

    ner_results = nlp(example)
    print(ner_results)"""

    """Speaker words"""
    #speaker_output = load_json_data(JSON_SPEAKER_TIME)
    #raw_output = load_json_data(JSON_RAW_OUTPUT)
    #output = combine_words_with_speakers(raw_output, speaker_output)

    #thing = merge_speaker_words(output)
    #write_json_data(JSON_SPEAKER_WORDS, output)

    """BART Summarizer"""    
    #modified_output = load_json_data(JSON_MODIFIED_OUTPUT)

    #summary_output = summarize_lines(modified_output)       
    #write_json_data(JSON_SUMMARY_OUTPUT, summary_output)

    """Speaker Diarization"""
    #speakers_dict = speaker_diarization(info_data['Wav'])
    #write_json_data(JSON_SPEAKER_TIME, speakers_dict)
    
    """PDF Extraction"""
    #pdf_output = extract_pdf_raw_text("Agenda_Items\Agenda_10.pdf")
    #result = extract_agenda_items(pdf_output)
    #JsonHelper.write_json_data("Agenda_09_Items.json", result)
    

    """Get Frame"""
    #get_frame_at_timestamp(info_data["Video"], "00:44:41.000", "test_frame_%03d.jpg")
    
    """Get Summaries of SRT"""
    srt_path = 'ASR_Whisperx/RegularCityCouncil-9_12_25.srt'
    agenda_path = "Agenda_Items/Agenda_12_Items.json"
    transcript = ""
    with open(srt_path, 'r', encoding='utf-8') as file:
        transcript += file.read()
        
    agenda_json = JsonHelper.load_json_data(agenda_path) or []
    
    # CHOICE OF ALL SUMMARIES METHOD
    # important_events = MeetingSummary.gen_important_events_from_srt(srt_path=srt_path)
    
    
    # SINGLE QUERY BY AGENDA AND HARDCODED FILTERS
    # filter_list = ['Policy', 'Civic', 'Voting']
    # filter_list = list(map(lambda a: f'{a['title']}', agenda_json))
    # additional_filters = ['Policy', 'Civic', 'Voting']
    # filter_list.extend(additional_filters)
    # important_events = MeetingSummary.gen_important_events_by_query(transcript=transcript, filter_list=filter_list, lines_per_chunk=30, max_query=5)
    
    
    
    
    
    # EMBED AND DOUBLE FILTER METHOD
    # filter by agenda titles
    # filter_list = list(map(lambda a: a['title'], agenda_json))
    # add extra filters if agenda is lackluster
    # additional_queries = ['Policy discussion', 'Civic discourse', 'Voting results or discussions']
    # filter_list.extend(additional_queries)
    # important_events = MeetingSummary.gen_important_events_by_double_query(transcript=transcript, filter_list=filter_list, init_lines_per_chunk=100, last_lines_per_chunk=25)
    
    
    
    
    
    # CLUSTER CENTROID METHOD
    important_events = MeetingSummary.get_important_events_by_cluster_centroids(transcript=transcript, lines_per_chunk=30, n_clusters=7)
    
    
    JsonHelper.write_json_data("Summaries/Summary-RegularCityCouncil-9_12_25.json", important_events)

if __name__ == '__main__':
    main() 