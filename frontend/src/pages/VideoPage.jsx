import dummysummaries from '@assets/dummysummaries.json'

import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import ReactPlayer from 'react-player';

import LoadingSpinner from "@components/icons/LoadingSpinner";

import Chatbot from "@components/Chatbot";
import { useRef } from 'react';
import VideoInfoCard from '@components/VideoInfoCard';
import { getTimezoneDate } from '@util/time';

const MEETING_ENDPOINT = "http://127.0.0.1:8000/getMeetingInfo";

// display videos alongside its transcript, agenda, bookmarks, and a chatbot
export default function VideoPage() {
    // id of the video being viewed
    const { id } = useParams();

    // data associated with the video needed for ReactPlayer
    const videoQuery = useQuery({ queryKey: ['videos', id], queryFn: fetchVideoData });

    const playerRef = useRef(null);

    async function fetchVideoData() {
        // would call api here in real implementation
        const res = await fetch(`${MEETING_ENDPOINT}/${id}`);
        if(!res.ok) throw new Error("Server error");
        const data = (await res.json())?.at(0);
        
        // TEMPORARY
        // INSERT SUMMARY DUMMY DATA
        // data.summaries = dummysummaries;

        if(!data) {
            throw new Error("Meeting not found");
        } else {
            return data;
        }
    }

    const handleTimeSelect = (sec) => {
        if(playerRef.current && sec >= 0) {
            // set the time of the video
            playerRef.current.currentTime = sec;
        }
    }


    // calculate date with timezone offset
    const dateObj = videoQuery.status === "success"
                    ? new Date(videoQuery.data.meeting.Date)
                    : null;

    const timezoneDateObj = getTimezoneDate(dateObj);
    return (
            <div className="container">
                {
                videoQuery.isPending ?
                <LoadingSpinner />
                : videoQuery.isError ?
                <div>An error occurred: {videoQuery.error.message}</div>
                :
                <>
                <div className="row mb-1">
                    <h2 className="text-start">{videoQuery.data.meeting.Title} - {timezoneDateObj.toLocaleDateString()}</h2>
                </div>
                <div className="row gap-3 mb-3">
                    <div className="col-lg-8">
                        {
                        videoQuery.data.meeting.VideoURL ?
                        <div className="rounded shadow overflow-hidden">
                            <ReactPlayer 
                                ref={playerRef}
                                src={videoQuery.data.meeting.VideoURL}
                                title={videoQuery.data.meeting.Title}

                                controls
                                style={{
                                    minWidth: "300px",
                                    width: "100%",
                                    height: "auto",
                                    aspectRatio: "16 / 9",
                                }}
                            />
                        </div>
                        :
                        <div className="my-3">No video could be found for this meeting</div>
                        }
                    </div>
                    <div className="col">
                        <Chatbot />
                    </div>
                </div>
                <div className="row">
                    <div className="col">
                        <VideoInfoCard 
                            videoData={videoQuery.data}
                            onTimeSelect={handleTimeSelect}
                        />
                    </div>
                </div>
                </>
                }
            </div>
    )
}
