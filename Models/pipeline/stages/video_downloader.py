from pytubefix import YouTube 
from pytubefix.cli import on_progress

from pipeline.orchestrator import PipelineStage
from pipeline.exceptions import PipelineError

class VideoDownloader(PipelineStage):
    def validate(self, input_data):
        return hasattr(input_data["videoUrl"])
    
    def execute(self, intput_data):
        try:
            video_url = intput_data["videoUrl"]

            yt = YouTube(video_url, on_progress_callback=on_progress)
            print(f"Got YouTube video\nTitle: {yt.title}")

            audio_stream = yt.streams.get_audio_only()

            return audio_stream.download()
        except Exception as e:
            raise PipelineError(f"Failed to download YouTube video: {e}")
    
    def cleanup(self):
        return super().cleanup()