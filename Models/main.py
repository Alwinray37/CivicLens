import json
import pymupdf
import torch
import torchaudio

import numpy as np

from dotenv import load_dotenv
import os

from pyannote.audio import Pipeline, Audio
from pyannote.core import Segment
from pyannote.audio.pipelines.utils.hook import ProgressHook

from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from faster_whisper import WhisperModel, BatchedInferencePipeline

from huggingface_hub import login

from tqdm import tqdm

JSON_INFO = 'info.json'
JSON_RAW_OUTPUT = 'output.json'
JSON_MODIFIED_OUTPUT = 'modifiedOutput.json'
JSON_SUMMARY_OUTPUT = 'summary.json'
JSON_SPEAKER_TIME = 'speaker_time.json'
JSON_SPEAKER_WORDS = 'speaker_words.json'

def load_json_data(json_filename):
    """
    Loads JSON data from a file.

    Args:
        json_filename (str): Path to the JSON file.

    Returns:
        dict or None: Parsed JSON data if successful, None otherwise.
    """
    try:
        with open(json_filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: '{json_filename}' not found")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{json_filename}'")
    # Return None if file not found or JSON is invalid
    return None

def write_json_data(json_filename, data):
    """
    Writes JSON data to a file.

    Args:
        json_filename (str): Path to the JSON file.
        data (dict): Data to write to the file.
    """
    with open(json_filename, 'w') as file:
        json.dump(data, file, indent=4)

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

def set_raw_output(audio_filename, model_size = 'medium'):
    """
    Transcribes audio using WhisperModel and saves word-level info to a JSON file.

    Args:
        audio_filename (str): Path to the audio file to transcribe.

    Returns:
        None
    """
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    batched_model = BatchedInferencePipeline(model=model)    
    segments, info = batched_model.transcribe(audio_filename, batch_size=16, word_timestamps=True, vad_filter=True)
    #segments, info = model.transcribe(audio_filename, word_timestamps=True, vad_filter=True)
    #segments = list(segments)


    word_info = []
    for segment in segments:
        for word in segment.words:
            word_info.append({'start': float(word.start), 'end': float(word.end), 'word': word.word})

    write_json_data(JSON_RAW_OUTPUT, word_info)   

def combine_words(data, max_time = 300):
    sentences = []

    current_line = {
        'text': "",
        'start': None,
        'end': None,
        'duration': 0.0,
        'words': []        
    }
    
    for i, word_data in enumerate(data):         
        word_text = word_data['word']    
        word_start = word_data['start']
        word_end = word_data['end']
        word_duration = word_end - word_start

        max_time_hit = current_line['duration'] >= max_time        

        if max_time_hit:
            sentences.append({
                'start': current_line['start'], 
                'end': current_line['end'], 
                'line': current_line['text'].strip(),
                'words': current_line['words']
                })

            current_line = {
                'text': "",
                'start': None,
                'end': None,
                'duration': 0.0,
                'words': []        
            }

        if current_line['start'] is None:
            current_line['start'] = word_start

        current_line['text'] += word_text
        current_line['end'] = word_end
        current_line['duration'] += word_duration
        current_line['words'].append({
            'text': word_text,
            'start': word_start,
            'end': word_end
        })            
        
        
    if current_line['text']:
        sentences.append({
            'start': current_line['start'], 
            'end': current_line['end'], 
            'line': current_line['text'].strip(),
            'words': current_line['words']
        })
      

    
    return sentences

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

def main():
    load_dotenv()

    """Uncomment to login to Huggingface"""
    #pyannote_token = os.getenv("PYANNOTE_TOKEN")
    #login(token=pyannote_token)

    info_data = load_json_data(JSON_INFO)

    if info_data is None:        
        return
    
    """Uncomment to Run ASR"""
    #set_raw_output(info_data['Filename'], model_size='small')    

    """Combine words into time segmented phrases"""
    #raw_output = load_json_data(JSON_RAW_OUTPUT)
    #processed_lines = combine_words(raw_output, info_data["MaxTime"])
    #write_json_data(JSON_MODIFIED_OUTPUT, processed_lines)

    """BERT Name Entity"""
    """
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")

    nlp = pipeline("ner", model=model, tokenizer=tokenizer)
    example = "My Alex is Wolfgang and I live in Berlin"

    ner_results = nlp(example)
    print(ner_results)"""

    speaker_output = load_json_data(JSON_SPEAKER_TIME)
    modified_output = load_json_data(JSON_RAW_OUTPUT)
    output = combine_words_with_speakers(modified_output, speaker_output)
    write_json_data(JSON_SPEAKER_WORDS, output)

    """BART Summarizer"""    
    #modified_output = load_json_data(JSON_MODIFIED_OUTPUT)

    #summary_output = summarize_lines(modified_output)       
    #write_json_data(JSON_SUMMARY_OUTPUT, summary_output)

    """Speaker Diarization"""
    #speakers_dict = speaker_diarization(info_data['Wav'])
    #write_json_data(JSON_SPEAKER_TIME, speakers_dict)
    


if __name__ == '__main__':
    main() 