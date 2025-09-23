import json
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
from faster_whisper import WhisperModel, BatchedInferencePipeline

JSON_INFO = 'info.json'
JSON_RAW_OUTPUT = 'output.json'
JSON_MODIFIED_OUTPUT = 'modifiedOutput.json'

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

def main():
    info_data = load_json_data(JSON_INFO)

    if info_data is None:        
        return
    
    """Uncomment to Run ASR"""
    #set_raw_output(info_data['Filename'], model_size='small')    


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

    """BART Summarizer"""    
    modified_output = load_json_data(JSON_MODIFIED_OUTPUT)

    summarizer = pipeline(task="summarization", model="sshleifer/distilbart-cnn-12-6")
    text = modified_output[0]['line']

    summarization_results = summarizer("PG&E stated it scheduled the blackouts in response to forecasts for high winds "
    "amid dry conditions. The aim is to reduce the risk of wildfires. Nearly 800 thousand customers were "
    "scheduled to be affected by the shutoffs which were expected to last through at least midday tomorrow.", max_length=28)
    print(summarization_results[0]["summary_text"])
    pass    

if __name__ == '__main__':
    main()