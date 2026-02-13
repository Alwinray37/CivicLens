import { forwardRef } from 'react';
import ReactPlayer from 'react-player';
import { PLAYER_CONFIG, PLAYER_STYLE } from '@util/videoPageUtility';

/**
 * Video player component that wraps ReactPlayer
 */
const VideoPlayer = forwardRef(({ videoURL, title }, ref) => {
    if (!videoURL) {
        return <div className="my-3">No video could be found for this meeting</div>;
    }

    return (
        <div className="rounded shadow overflow-hidden">
            <ReactPlayer 
                ref={ref}
                src={videoURL}
                title={title}
                controls={true}
                config={PLAYER_CONFIG}
                style={PLAYER_STYLE}
            />
        </div>
    );
});

VideoPlayer.displayName = 'VideoPlayer';

export default VideoPlayer;
