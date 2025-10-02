import { useParams } from "react-router-dom";
import ReactPlayer from 'react-player';
import { useEffect, useState } from "react";

import Chatbot from "./Chatbot";
import TranscriptCard from "./TranscriptCard";
import AgendaCard from "./AgendaCard";
import BookmarkCard from "./BookmarkCard";

/*
    * Display of individual videos alongside 
    * its transcript, agenda, bookmarks, and a chatbot
*/
export default function VideoPage() {
    // id of the video being viewed
    const { id } = useParams();
    // data associated with the video needed for ReactPlayer
    const [videoData, setVideoData] = useState({
        src: undefined,
    });

    // fetch the video data on mount
    useEffect(() => {
        function fetchVideoData() {
            // would call api here in real implementation
            setTimeout(() => {
                setVideoData((curData) => ({
                    ...curData,
                    src: "https://youtube.com/watch?v=BBm5RCvC0TU",
                }));
            }, 300)
        }

        fetchVideoData();
    }, []);

    return (
            <div className="container">
                <div className="row gap-3 row-cols-1 row-cols-lg-2 justify-content-center">
                    <div className="col col-lg-8 d-flex flex-column gap-3 flex-grow-1 ">
                        <ReactPlayer src={videoData.src} 
                            style={{
                                minWidth: "300px",
                                width: "100%",
                                height: "auto",
                                aspectRatio: "16 / 9",
                            }}
                        />
                        <TranscriptCard snippets={[
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            },
                            {
                                time: "2:57",
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                            }
                        ]}/>
                    </div>
                    <div className="col col-lg-3 d-flex flex-column gap-3 flex-grow-1 ">
                        <Chatbot />
                        <AgendaCard events={[
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                            {
                                content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                                timespan: "0:00-5:00",
                            },
                        ]}/>
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
            </div>
    )
}
