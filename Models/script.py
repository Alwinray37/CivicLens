# City council meetings Tuesday, Wednesday and Friday at 10:00 am

# Argparse command for server? 

# ✓
# Call meeting link, grab last json record from the array, comitteeId: 1 is for City Council Meeting, ignore "-SAP" since spanish
# Meeting link: https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={year} 

# use pytube to download video
# agenda items link: https://lacity.primegov.com/Public/CompiledDocument?meetingTemplateId={templateId}&compileOutputType={compileoutputtype}

# call models to get the transcript data
# get the pdf agenda and parse through it

# call embedding model to get embedding data
# generate sql table script for static db generation

# delete extra files generated - mp3, jsons, and etc

import os
import ffmpeg
import requests
from pytubefix import YouTube
from pytubefix.cli import on_progress

MEETING_YEAR = 2026 #temp, maybe argparse idk lol

COUNCIL_MEETINGS_ID = 1
NO_SAP = "SAP"
CITY_COUNCIL_URL = f"https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={MEETING_YEAR}"

def Grab_Meetings():
    try:
        response = requests.get(CITY_COUNCIL_URL)

        if response.status_code == 200:
            meetings_data = response.json()

            council_meetings = list(filter(lambda meeting: meeting["meetingTypeId"] == COUNCIL_MEETINGS_ID and meeting["title"] not in NO_SAP, meetings_data))

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

def Convert_M4A_to_MP3(input_file, output_file):
    try:
        ffmpeg.input(input_file).output(output_file, codec='libmp3lame', q=4).run(quiet=True, overwrite_output=True)
        return output_file
    except Exception as e:
        print(f"An error occured: {e}")
        raise

print(f"Getting meetings")
latest_meeting = Grab_Meetings()[-1]

print(f"Getting YouTube video")
video_url = latest_meeting["videoUrl"]

print(f"Starting Youtube video download")
m4a_audio_file = Download_Youtube_Video(video_url)
print(f"Download complete")

print(f"Converting M4A to MP3")
mp3_audio_file = Convert_M4A_to_MP3(m4a_audio_file, "temp_mp3_audio.mp3")
print(f"Conversion complete")

print(latest_meeting)