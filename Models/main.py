import torch
import torchaudio
import ffmpeg

from utils.json_helper import JsonHelper
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
from utils.pdf_extraction import PdfExtraction

JSON_INFO = 'info.json'
JSON_RAW_OUTPUT = 'output.json'
JSON_MODIFIED_OUTPUT = 'modifiedOutput.json'
JSON_SUMMARY_OUTPUT = 'summary.json'
JSON_SPEAKER_TIME = 'speaker_time.json'
JSON_SPEAKER_WORDS = 'speaker_words.json'
JSON_PDF_EXTRACTION = 'pdf_extraction.json'

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
    #pdf_output = PdfExtraction.extract_pdf_raw_text("Agenda_Items\Minutes_12.pdf")
    #result = PdfExtraction.extract_minutes_structured(pdf_output)
    #JsonHelper.write_json_data("Minutes_12.json", result)    
    

    """Get Frame"""
    #get_frame_at_timestamp(info_data["Video"], "00:44:41.000", "test_frame_%03d.jpg")
    
    """Get Summaries of SRT"""
    srt_path = 'ASR_Whisperx/RegularCityCouncil-9_9_25.srt'
    meeting_json_path =  'ASR_Whisperx/RegularCityCouncil-9_12_25.json'
    agenda_path = "Agenda_Items/Agenda_12_Items.json"
    minutes_path = "Agenda_Items/Minutes_12.json"
        
    agenda_json = JsonHelper.load_json_data(agenda_path) or []
    minutes_json = JsonHelper.load_json_data(minutes_path) or []

    m_sum = MeetingSummary(meeting_json_path=meeting_json_path, 
                          chunk_sum_model=MeetingSummary.summary_models["llama-8b"], 
                          fin_select_model=MeetingSummary.summary_models["llama-8b"],
                          emb_model=MeetingSummary.embedding_models["qwen-4b"])
    
    m_sum.chunk_opts = {
            'method': 'fixed',
            'delim': '\n',
            'lines_per_chunk': 50,
            'overlap': 5,
            }

    # CHOICE OF ALL SUMMARIES METHOD
    # important_events = m_sum.gen_important_events(lines_per_chunk=30)

    # ASR SEGMENTATION
    # m_sum.gen_meeting_asr_segmentation(json_agenda=agenda_json, json_minutes=minutes_json, lines_per_chunk=1)
    
    # SINGLE QUERY BY AGENDA AND HARDCODED FILTERS
    filter_list = ['Policy', 'Civic', 'Voting']
    filter_list = list(map(lambda a: a['title'], agenda_json))
    additional_filters = ['Policy', 'Civic', 'Voting']
    filter_list.extend(additional_filters)
    important_events = m_sum.gen_important_events_by_query(filter_list=filter_list, max_query=5)
    print(important_events)
    
    
    
    
    
    # EMBED AND DOUBLE FILTER METHOD
    # filter by agenda titles
    # filter_list = list(map(lambda a: a['title'], agenda_json))
    # add extra filters if agenda is lackluster
    # additional_queries = ['Policy discussion', 'Civic discourse', 'Voting results or discussions']
    # filter_list.extend(additional_queries)
    # important_events = m_sum.gen_important_events_by_double_query(filter_list=filter_list, init_lines_per_chunk=100, last_lines_per_chunk=25)
    
    
    
    
    
    # CLUSTER CENTROID METHOD
    # important_events = m_sum.get_important_events_by_cluster_centroids(lines_per_chunk=30, n_clusters=7)
    
    
    # JsonHelper.write_json_data("Summaries/70b_Summary-RegularCityCouncil-9_9_25.json", important_events)

if __name__ == '__main__':
    main() 
