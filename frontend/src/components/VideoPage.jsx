import { useParams } from "react-router-dom";
import ReactPlayer from 'react-player';
import { useEffect, useState } from "react";

import styles from './VideoPage.module.css';
import Chatbot from "./Chatbot";
import TranscriptCard from "./TranscriptCard";
import AgendaCard from "./AgendaCard";
import BookmarkCard from "./BookmarkCard";

export default function VideoPage() {
    const { id } = useParams();
    const [videoData, setVideoData] = useState({
        src: undefined,
    });

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
        <div className={"p-3 overflow-scroll " + styles.videoPage}>
            <div className="container">
                <div className="row gap-3 row-cols-1 row-cols-md-2 mb-3 justify-content-between">
                    <div className="col col-md-8">
                            <ReactPlayer src={videoData.src} 
                                style={{
                                    minWidth: "300px",
                                    width: "100%",
                                    height: "auto",
                                    aspectRatio: "16 / 9",
                                }}
                            />
                    </div>
                    <div className="col col-md-3">
                        <Chatbot />
                    </div>
                </div>
                <div className="row row-cols-1 row-cols-md-2 justify-content-between">
                    <div className="col col-md-8 mb-3">
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
                    <div className="col col-md-3 mb-3">
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
                    </div>
                </div>
                <div className="row">
                    <div className="col">
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
        </div>
    )
}
