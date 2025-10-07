import { useParams, useLocation,  } from "react-router-dom";
import ReactPlayer from 'react-player';
import { useEffect, useState } from "react";

import Chatbot from "./Chatbot";
import TranscriptCard from "./TranscriptCard";
import AgendaCard from "./AgendaCard";
import BookmarkCard from "./BookmarkCard";

export default function VideoPage() {
    const { id } = useParams();
    const [videoData, setVideoData] = useState({
        src: undefined,
    });
    // this is data passed from the CatalogPage when navigating to this page
    // found in handleButtonClick function
    const location = useLocation();
    const videoID = location.state?.videoId || id;
    const videoURL = location.state?.videoUrl || null;
    console.log("Video ID:", videoID);
    console.log("Video url:", videoURL);

    useEffect(() => {
        function fetchVideoData() {
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
                        <ReactPlayer src={videoURL} controls={true}
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
