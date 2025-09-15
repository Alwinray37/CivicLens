import json
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

def main():
    info_data = load_json_data(JSON_INFO)

    if info_data is None:        
        return
    
    set_raw_output(info_data['Filename'], model_size='small')    

    pass

if __name__ == '__main__':
    main()