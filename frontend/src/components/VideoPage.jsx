import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import ReactPlayer from 'react-player';

import LoadingSpinner from "./icons/LoadingSpinner";

import Chatbot from "./Chatbot";
import { useRef } from 'react';
import VideoInfoCard from './VideoInfoCard';

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
        const data = await res.json();

        if(!data || !data[0]) {
            throw new Error("Meeting not found");
        } else {
            return data[0];
        }
    }

    const handleTimeSelect = (sec) => {
        if(playerRef.current && sec >= 0) {
            // set the time of the video
            playerRef.current.currentTime = sec;
        }
    }

    return (
            <div className="container">
                {
                videoQuery.isPending ?
                <LoadingSpinner />
                : videoQuery.isError ?
                <div>An error occurred: {videoQuery.error.message}</div>
                :
                <>
                <div className="row gap-3 mb-3">
                    <div className="col-lg-8">
                        {
                        videoQuery.data.meeting.VideoURL ?
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
