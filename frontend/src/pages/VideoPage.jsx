import { useParams } from "react-router-dom";
import { useRef } from 'react';

import LoadingSpinner from "@components/icons/LoadingSpinner";
import ErrorMessage from "@components/ErrorMessage";
import Chatbot from "@components/Chatbot";
import VideoInfoCard from '@components/VideoInfoCard';
import VideoPlayer from '@components/VideoPlayer';

import { useVideoData } from '@hooks/useVideoData';
import { getTimezoneDate } from '@util/time';

/**
 * VideoPage displays videos alongside meeting details and a chatbot
 */
export default function VideoPage() {
    const { id } = useParams();
    const playerRef = useRef(null);
    const videoQuery = useVideoData(id);

    // Early returns for loading and error states
    if (videoQuery.isPending) {
        return (
            <div className="container">
                <LoadingSpinner />
            </div>
        );
    }

    if (videoQuery.isError) {
        return (
            <div className="container">
                <ErrorMessage error={videoQuery.error} />
            </div>
        );
    }

    const { meeting } = videoQuery.data;
    const timezoneDateObj = getTimezoneDate(new Date(meeting.Date));

    /**
     * Handles time selection from VideoInfoCard
     * @param {number} sec - Time in seconds to seek to
     */
    const handleTimeSelect = (sec) => {
        if (playerRef.current && sec >= 0) {
            // Access the API from the player element
            const player = playerRef.current.api || playerRef.current;
            if (player && typeof player.seekTo === 'function') {
                player.seekTo(sec, 'seconds');
            } else if (player && player.currentTime !== undefined) {
                // Fallback for native HTML5 video element
                player.currentTime = sec;
            }
        }
    };

    return (
        <div className="container">
            <div className="row mb-1">
                <h2 className="text-start">
                    {meeting.Title} - {timezoneDateObj.toLocaleDateString()}
                </h2>
            </div>
            
            <div className="row gap-3 mb-3">
                <div className="col-lg-8">
                    <VideoPlayer 
                        ref={playerRef}
                        videoURL={meeting.VideoURL}
                        title={meeting.Title}
                    />
                </div>
                <div className="col">
                    <Chatbot 
                        meetingId={id}
                        onTimeSelect={handleTimeSelect}
                    />
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
        </div>
    );
}
