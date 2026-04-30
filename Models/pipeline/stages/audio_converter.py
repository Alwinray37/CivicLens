import subprocess
from pathlib import Path

from pipeline.stage import PipelineStage
from pipeline.exceptions import PipelineError

class AudioConverter(PipelineStage):
    def __init__(self, config):
        super().__init__(config)
        self.m4a_file_path = None
    
    def validate(self, input_data):
        """Validate that input is a valid m4a file."""
        if not isinstance(input_data, (str, Path)):
            self.logger.warning(f"Input must be a file path string or Path object, got {type(input_data)}")
            return False
        
        file_path = Path(input_data)
        
        if not file_path.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return False
        
        if file_path.suffix.lower() != '.m4a':
            self.logger.warning(f"File must have .m4a extension, got {file_path.suffix}")
            return False
        
        # Check magic bytes (m4a files start with 'ftyp' signature)
        try:
            with open(file_path, 'rb') as f:
                # Skip first 4 bytes, then check for 'ftyp'
                f.seek(4)
                magic = f.read(4)
                if magic != b'ftyp':
                    self.logger.warning(f"File magic bytes do not match m4a format: {magic}")
                    return False
        except Exception as e:
            self.logger.warning(f"Failed to read file magic bytes: {e}")
            return False
        
        return True
    
    def execute(self, input_data):
        try:
            self.m4a_file_path = input_data

            output_file = input_data.replace(".m4a", ".mp3")

            command = [
                "ffmpeg",
                "-i", input_data,
                "-c:a", "libmp3lame",
                "-q:a", "4",
                output_file
            ]
            
            subprocess.run(command, check=True)

            self.logger.info(f"Successfully converted {input_data} to {output_file}")
            return output_file
        except Exception as e:
            raise PipelineError(f"Failed converting M4A file to MP3: {e}")
    
    def cleanup(self):
        """Remove the m4a file after conversion."""
        if self.m4a_file_path and Path(self.m4a_file_path).exists():
            try:
                Path(self.m4a_file_path).unlink()
                self.logger.info(f"Removed m4a file: {self.m4a_file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to remove m4a file {self.m4a_file_path}: {e}")