# City council meetings Tuesday, Wednesday and Friday at 10:00 am

# Argparse command for server? 

# ✓
# Call meeting link, grab last json record from the array, comitteeId: 1 is for City Council Meeting, ignore "-SAP" since spanish
# Meeting link: https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={year} 

# ✓
# use pytube to download video

# agenda items link: https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId={templateId}&compileOutputType={compileoutputtype}

# call models to get the transcript data
# get the pdf agenda and parse through it

# call embedding model to get embedding data
# generate sql table script for static db generation

# delete extra files generated - mp3, jsons, and etc

import os
import subprocess
import requests
from pydub import AudioSegment
from pytubefix import YouTube
from pytubefix.cli import on_progress

from json_helper import JsonHelper
from pdf_extraction import PdfExtraction

MEETING_YEAR = 2026 #temp, maybe argparse idk lol

COUNCIL_MEETINGS_ID = 1
NO_SAP = "SAP"
AGENDA = "Agenda"
CITY_COUNCIL_URL = f"https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={MEETING_YEAR}"

def Grab_Meetings():
    try:
        response = requests.get(CITY_COUNCIL_URL)

        response.raise_for_status()

        meetings_data = response.json()

        council_meetings = list(filter(lambda meeting: meeting["meetingTypeId"] == COUNCIL_MEETINGS_ID 
                                        and meeting["title"] not in NO_SAP 
                                        and meeting["videoUrl"]
                                        and filter(lambda document: document["templateName"] == AGENDA
                                                    , meeting["documentList"])
                                        , meetings_data))

        return council_meetings

    except Exception as e:
        print(f"An error occured: {e}")
        raise

def Download_Youtube_Video(video_url):
    try:
        yt = YouTube(video_url, on_progress_callback=on_progress)
        print(f"Got YouTube video\nTitle: {yt.title}")

        audio_stream = yt.streams.get_audio_only()

        return audio_stream.download()
    except Exception as e:
        print(f"An error occured: {e}")
        raise

def Download_PDF(meeting):
    agendaInfo = list(filter(lambda document: document["templateName"] == AGENDA, 
                         meeting["documentList"]))[0]

    templateId = agendaInfo["templateId"]
    compileOutputType = agendaInfo["compileOutputType"]

    agenda_path = f"agenda_{meeting['id']}.pdf"

    AGENDA_URL = f"https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId={templateId}&compileOutputType={compileOutputType}"
    try:
        response = requests.get(AGENDA_URL, stream=True)

        response.raise_for_status()

        with open(agenda_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return agenda_path
    except Exception as e:
        print(f"An error occured: {e}")
        raise

def Convert_M4A_to_MP3(input_file, output_file = None):
    try:
        if output_file is None:
            output_file = input_file.replace(".m4a", ".mp3")
        
        input_sound = AudioSegment.from_file(input_file, format="m4a")
        input_sound.export(output_file, format="mp3")

        return output_file
    except Exception as e:
        print(f"An error occured: {e}")
        raise

print(f"Getting meetings")
last_meeting = Grab_Meetings()[-1]

print(f"Getting YouTube video")
video_url = last_meeting["videoUrl"]

print(f"Starting Youtube video download")
#m4a_audio_file = Download_Youtube_Video(video_url)
print(f"Download complete")

#TEMP
#m4a_audio_file = os.path.join(os.getcwd(), "Regular City Council - 3626.m4a")
#TEMP

#print(os.path.exists(m4a_audio_file))

print(f"Converting M4A to MP3")
#mp3_audio_file = Convert_M4A_to_MP3(m4a_audio_file)
print(f"Conversion complete")

print(f"Getting Downloading Agenda PDf")
agenda_file = Download_PDF(last_meeting)
print(f"Downloaded Agenda PDF")

print(f"Parsing PDF Agenda items to JSON")
pdf_raw_text = PdfExtraction.extract_pdf_raw_text(agenda_file)
result = PdfExtraction.extract_minutes_structured(pdf_raw_text)
JsonHelper.write_json_data(agenda_file + ".json", result)    
print(f"Parsing complete from PDF to JSON")

print(last_meeting)