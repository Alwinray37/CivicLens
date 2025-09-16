// Video List Page Component
// this will list the video as cards for users to click on and watch
// when clicked, it will take the user to the video watch page
import dummydata from '../assets/dummydata.json';

export default function VideoListPage() {
    const videoList = dummydata; 

    return (
        <div className="container" id="video-list-page">
            <h1>Civic Meetings</h1>
            <div className="video-card-list container">
                {videoList.map((video) => (
                    <div className="video-card" key={video.id}>
                        <img src={video.thumbnail} alt={video.title} className="thumbnail" />
                        <h2 className="title">{video.title}</h2>
                        <p className="description">{video.description}</p>
                    </div>
                ))}
            </div>
        </div>
    )
}