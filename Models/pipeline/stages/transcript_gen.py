import os
import torch
import subprocess

from pathlib import Path
from pipeline.exceptions import PipelineError
from pipeline.stage import PipelineStage

class TranscriptGen(PipelineStage):
    def validate(self, input_data):
        """Validate that input_data is a path to an MP3 file."""
        if not isinstance(input_data, str):
            self.logger.error("Input must be a file path string")
            return False
        
        if not os.path.exists(input_data):
            self.logger.error(f"File does not exist: {input_data}")
            return False
        
        if not input_data.lower().endswith('.mp3'):
            self.logger.error(f"File is not an MP3 file: {input_data}")
            return False
        
        # Verify MP3 file signature (magic bytes)
        try:
            with open(input_data, 'rb') as f:
                header = f.read(3)
                # Check for MP3 ID3 tag or MPEG sync word
                if not (header[:2] == b'ID' or header[0:1] == b'\xff'):
                    self.logger.error("File does not have valid MP3 format")
                    return False
        except Exception as e:
            self.logger.error(f"Error reading file: {e}")
            return False
        
        return True
    
    def execute(self, intput_data):
        if not torch.cuda.is_available():
            raise PipelineError(f"Cude not available for meeting transcript generation")

        # Use WhisperX CLI to generate all formats
        cmd = [
            "whisperx",
            intput_data,
            "--model", "large-v2",
            "--device", "cuda",
            "--language", "en",
            "--compute_type", self.config.compute_type,
            "--batch_size", self.config.batch_size,
            "--hf_token", self.config.pyannote_token,
            "--output_format", "all",  # Generates srt, vtt, txt, json, tsv
            "--output_dir", str(self.config.temp_dir),
            "--diarize"
        ]
    
        result = subprocess.run(cmd, check=True)
        
        if result.returncode != 0:
            raise PipelineError(f"WhisperX failed")

        input_path = Path(intput_data)
        json_file = Path(self.config.temp_dir) / f"{input_path.stem}.json"

        return str(json_file)
    
    def cleanup(self):
        """No clean up, keep all the files"""
        pass