from faster_whisper import WhisperModel, BatchedInferencePipeline

class AsrExtraction:
    def __init__(self, raw_ouput = None):
        self._raw_output = raw_ouput
        pass

    def set_raw_output(self, audio_filename, model_size = 'medium'):
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

        self._raw_output = word_info
        return word_info      

    def combine_words(self, data = None, max_time = 300):        
        if data is None:
            data = self._raw_output

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