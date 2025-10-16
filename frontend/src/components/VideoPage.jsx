import dummydata from '../assets/dummydata.json';
import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import ReactPlayer from 'react-player';

import LoadingSpinner from "./icons/LoadingSpinner";

import Chatbot from "./Chatbot";
import TranscriptCard from "./TranscriptCard";
import AgendaCard from "./AgendaCard";
import BookmarkCard from "./BookmarkCard";
import { useRef } from 'react';

// display videos alongside its transcript, agenda, bookmarks, and a chatbot
export default function VideoPage() {
    // id of the video being viewed
    const { id } = useParams();

    // data associated with the video needed for ReactPlayer
    const videoQuery = useQuery({ queryKey: ['videos', id], queryFn: fetchVideoData });

    const playerRef = useRef(null);

    async function fetchVideoData() {
        // would call api here in real implementation

        // currently retrieving video obj from dummydata 
        const video = dummydata.find((v) => v.id.toString() === id);
        if(!video) {
            throw new Error("Meeting not found");
        } else {
            return video;
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
                <div className="row gap-3 row-cols-1 row-cols-lg-2 justify-content-center">
                    <div className="col col-lg-8 d-flex flex-column gap-3 flex-grow-1 ">
                        {
                        videoQuery.data.videoUrl ?
                        <ReactPlayer 
                            ref={playerRef}
                            src={videoQuery.data.videoUrl}
                            title={videoQuery.data.title}
                            
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
                        <TranscriptCard 
                            onItemClick={handleTimeSelect}
                            snippets={[
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "5:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "10:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "20:00",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                        ]}/>
                    </div>
                    <div className="col col-lg-3 d-flex flex-column gap-3 flex-grow-1 ">
                        <Chatbot />
                        <AgendaCard 
                            events={[
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "2:10-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "10:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                        ]}
                        onItemClick={handleTimeSelect}
                        />
                        <BookmarkCard bookmarks={[
                            {
                                title: "Smith Opposition Statement",
                                description: "Key opposition points",
                                time: "60:20",
                            },
                            {
                                title: "Smith Opposition Statement",
                                description: "Key opposition points",
                                time: "60:20",
                            },
                            {
                                title: "Smith Opposition Statement",
                                description: "Key opposition points",
                                time: "60:20",
                            },
                            {
                                title: "Smith Opposition Statement",
                                description: "Key opposition points",
                                time: "60:20",
                            },
                            {
                                title: "Smith Opposition Statement",
                                description: "Key opposition points",
                                time: "60:20",
                            },
                            {
                                title: "Smith Opposition Statement",
                                description: "Key opposition points",
                                time: "60:20",
                            },
                        ]}/>
                    </div>
                </div>
                }
            </div>
    )
}
