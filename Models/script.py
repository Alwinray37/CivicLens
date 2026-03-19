# City council meetings Tuesday, Wednesday and Friday at 10:00 am

# Argparse command for server? 

# ✓
# Call meeting link, grab last json record from the array, comitteeId: 1 is for City Council Meeting, ignore "-SAP" since spanish
# Meeting link: https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={year} 

# ✓
# use pytube to download video

# ✓
# agenda items link: https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId={templateId}&compileOutputType={compileoutputtype}

# ✓
# get the pdf agenda and parse through it

# call models to get the transcript data

# call embedding model to get embedding data
# generate sql table script for static db generation

# delete extra files generated - mp3, jsons, and etc

from pipeline.config import PipelineConfig
from pipeline.orchestrator import PipelineOrchestrator

if __name__ == "__main__":
    config = PipelineConfig(meeting_year=2026, enable_cleanup=False)
    orchestrator = PipelineOrchestrator(config)
    orchestrator.execute()