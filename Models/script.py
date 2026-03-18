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

import os
import requests
import logging
from pydub import AudioSegment

# Using pytubefix because pytube is deprecated/broken
from pytubefix import YouTube 
from pytubefix.cli import on_progress

from json_helper import JsonHelper
from pdf_extraction import PdfExtraction

MEETING_YEAR = 2026 #temp, maybe argparse idk lol

COUNCIL_MEETINGS_ID = 1
NO_SAP = "SAP"
AGENDA = "Agenda"
CITY_COUNCIL_URL = f"https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={MEETING_YEAR}"

logger = logging.getLogger(__name__)

def grab_meetings():
    try:
        response = requests.get(CITY_COUNCIL_URL, timeout=30)

        response.raise_for_status()

        meetings_data = response.json()

        council_meetings = list(filter(lambda meeting: meeting["meetingTypeId"] == COUNCIL_MEETINGS_ID 
                                        and meeting["title"] not in NO_SAP 
                                        and meeting["videoUrl"]
                                        and any(doc["templateName"] == AGENDA for doc in meeting["documentList"])
                                        , meetings_data))

        return council_meetings

    except requests.HTTPError as e:
        print(f"An error occured: {e}")
        raise

def download_youtube_video(video_url):
    try:
        yt = YouTube(video_url, on_progress_callback=on_progress)
        print(f"Got YouTube video\nTitle: {yt.title}")

        audio_stream = yt.streams.get_audio_only()

        return audio_stream.download()
    except Exception as e:
        print(f"An error occured: {e}")
        raise

def download_pDF(meeting):
    matching_docs = [d for d in meeting["documentList"] if d["templateName"] == AGENDA]
    if not matching_docs:
        raise ValueError(f"No agenda document found for meeting {meeting['id']}")

    agendaInfo = list(filter(lambda document: document["templateName"] == AGENDA, 
                         meeting["documentList"]))[0]

    templateId = agendaInfo["templateId"]
    compileOutputType = agendaInfo["compileOutputType"]

    agenda_path = f"agenda_{meeting['id']}.pdf"

    AGENDA_URL = f"https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId={templateId}&compileOutputType={compileOutputType}"
    try:
        response = requests.get(AGENDA_URL, stream=True, timeout=30)

        response.raise_for_status()

        with open(agenda_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return agenda_path
    except Exception as e:
        print(f"An error occured: {e}")
        raise

def convert_m4a_to_mp3(input_file, output_file = None):
    try:
        if output_file is None:
            output_file = input_file.replace(".m4a", ".mp3")
        
        input_sound = AudioSegment.from_file(input_file, format="m4a")
        input_sound.export(output_file, format="mp3")

        return output_file
    except Exception as e:
        print(f"An error occured: {e}")
        raise

if __name__ == "__main__":
    try:
        logger.info("Getting meetings...")
        last_meeting = grab_meetings()[-1]

        logger.info("Getting YouTube video")
        video_url = last_meeting["videoUrl"]

        logger.info("Starting Youtube video download")
        m4a_audio_file = download_youtube_video(video_url)
        logger.info("Download complete")

        #TEMP
        #m4a_audio_file = os.path.join(os.getcwd(), "Regular City Council - 3626.m4a")
        #TEMP

        logger.info("Converting M4A to MP3")
        mp3_audio_file = convert_m4a_to_mp3(m4a_audio_file)
        logger.info("Conversion complete")

        logger.info("Getting Downloading Agenda PDf")
        agenda_file = download_pDF(last_meeting)
        logger.info("Downloaded Agenda PDF")

        logger.info("Parsing PDF Agenda items to JSON")
        pdf_raw_text = PdfExtraction.extract_pdf_raw_text(agenda_file)
        result = PdfExtraction.extract_minutes_structured(pdf_raw_text)
        JsonHelper.write_json_data(agenda_file + ".json", result)    
        logger.info("Parsing complete from PDF to JSON")

        logger.info(last_meeting)
    except Exception as e:
        logger.critical(f"Pipeline failed: {e}")