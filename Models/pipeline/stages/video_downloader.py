from pytubefix import YouTube 
from pytubefix.cli import on_progress

from pipeline.stage import PipelineStage
from pipeline.exceptions import PipelineError

class VideoDownloader(PipelineStage):
    def validate(self, input_data):
        return "videoUrl" in input_data
    
    def execute(self, intput_data):
        try:
            video_url = intput_data["videoUrl"]

            yt = YouTube(video_url, on_progress_callback=on_progress)
            self.logger.info(f"Got YouTube video\nTitle: {yt.title}")

            audio_stream = yt.streams.get_audio_only()
            downloaded_path = audio_stream.download(output_path=str(self.config.temp_dir))

            return str(downloaded_path)
        except Exception as e:
            raise PipelineError(f"Failed to download YouTube video: {e}")
    
    def cleanup(self):
        return super().cleanup()