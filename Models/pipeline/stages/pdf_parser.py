from pathlib import Path

from utils.pdf_extraction import PdfExtraction
from utils.json_helper import JsonHelper

from pipeline.exceptions import PipelineError
from pipeline.stage import PipelineStage

class PdfParser(PipelineStage):
    def __init__(self, config):
        super().__init__(config)
        self.pdf_file_path = None
    
    def validate(self, input_data):
        """Validate that input is a valid PDF file."""
        if not isinstance(input_data, (str, Path)):
            self.logger.warning(f"Input must be a file path string or Path object, got {type(input_data)}")
            return False
        
        file_path = Path(input_data)
        
        if not file_path.exists():
            self.logger.warning(f"File does not exist: {file_path}")
            return False
        
        if file_path.suffix.lower() != '.pdf':
            self.logger.warning(f"File must have .pdf extension, got {file_path.suffix}")
            return False
        
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                if magic != b'%PDF':
                    self.logger.warning(f"File magic bytes do not match PDF format: {magic}")
                    return False
        except Exception as e:
            self.logger.warning(f"Failed to read file magic bytes: {e}")
            return False
        
        return True
    
    def execute(self, intput_data):
        self.pdf_file_path = Path(intput_data)
        
        jsonFile = self.config.output_dir / f"{self.pdf_file_path.stem}_parsed.json"
        try:
            pdf_raw_text = PdfExtraction.extract_pdf_raw_text(intput_data)
            result = PdfExtraction.extract_minutes_structured(pdf_raw_text)
            JsonHelper.write_json_data(jsonFile, result)

            return jsonFile
        except Exception as e:
            raise PipelineError(f"Failed to convert pdf file to Json: {e}")

    def cleanup(self):
        """Remove the PDF file after parsing."""
        if self.pdf_file_path and Path(self.pdf_file_path).exists():
            try:
                Path(self.pdf_file_path).unlink()
                self.logger.info(f"Removed PDF file: {self.pdf_file_path}")
            except Exception as e:
                self.logger.warning(f"Failed to remove PDF file {self.pdf_file_path}: {e}")
        