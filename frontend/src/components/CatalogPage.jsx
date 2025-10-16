// Catalog Page Component
// this will list the video as cards for users to click on and watch
// when clicked, it will take the user to the video watch page
import dummydata from '../assets/dummydata.json';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import LoadingSpinner from './icons/LoadingSpinner';

const CATALOG_ENDPOINT = "http://127.0.0.1:8000/getMeetings";

export default function VideoListPage() {
    const [dateOrder, setDateOrder] = useState('desc');
    const [filterTag, setFilterTag] = useState('');
    const [search, setSearch] = useState('');

    const navigate = useNavigate();

    const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalogData });

    // fetches meetings in the catalog
    async function fetchCatalogData() {
        try {
            const res = await fetch(CATALOG_ENDPOINT);
            if(!res.ok) {
                // tanstack requires data to be returned or
                // an error to be thrown in the queryFn
                throw new Error("Server error");
            }

            const data = await res.json();
            return data;
        } catch(err) {
            throw new Error(err);
        }
    }

    let filteredList;

    // Get all unique tags from the data (not yet available)
    let allTags = Array.from(new Set(dummydata.flatMap(video => video.tags || [])));

    if(catalogQuery.status === "success") {
        // filter the data from dummydata, retrieve only the videos that have a videoUrl
        filteredList = catalogQuery.data.data[0][0].filter(video => {
            if (video.VideoUrl === null) return false;
            // no tags yet
            // const tagMatch = filterTag ? (video.tags || []).includes(filterTag) : true;
            const tagMatch = true; // TEMP
            // Search in title or tags
            const searchLower = search.toLowerCase();
            const titleMatch = video.Title.toLowerCase().includes(searchLower);
            // const tagsMatch = (video.tags || []).some(tag => tag.toLowerCase().includes(searchLower));
            // const searchMatch = search ? (titleMatch || tagsMatch) : true;
            const searchMatch = search ? titleMatch : true;
            return tagMatch && searchMatch;
        })
        .sort((a, b) => { // Sort by date
            if (!a.date || !b.date) return 0;
            if (dateOrder === 'asc') {
                return new Date(a.date) - new Date(b.date);
            } else {
                return new Date(b.date) - new Date(a.date);
            }
        });
    }


    // handle button click to open video page 
    // navigates to /watch/:id route with videoId as param
    const handleButtonClick = (videoId, videoUrl) => {
        navigate (`/watch/${videoId}`, { state: { videoId, videoUrl } });
    }

    return (
        <div className="container" id="video-list-page">
            <div className="heading d-flex align-items-center justify-content-between">
                <h1>Civic Meetings</h1>
                <div className="filter d-flex gap-2">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search title or tags..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        style={{ maxWidth: '180px' }}
                    />
                    <select
                        className="form-select"
                        value={filterTag}
                        onChange={e => setFilterTag(e.target.value)}
                        style={{ maxWidth: '140px' }}
                    >
                        <option value="">All Tags</option> {/* need to add tags when available */}
                        {allTags.map(tag => (
                            <option key={tag} value={tag}>{tag}</option>
                        ))}
                    </select>
                    {/* might change this to a toggle button */}
                    <select
                        className="form-select"
                        value={dateOrder}
                        onChange={e => setDateOrder(e.target.value)}
                        style={{ maxWidth: '140px' }}
                    >
                        <option value="desc">Newest First</option>
                        <option value="asc">Oldest First</option>
                    </select>
                    <button className="btn btn-secondary" onClick={() => { setSearch(''); setFilterTag(''); setDateOrder('desc'); }}>Clear</button>
                </div>
            </div>

            <div className="video-card-list container">
                {
                filteredList ?
                    filteredList.length > 0 ?
                    filteredList.map((video) => (
                        <div className="video-card d-flex flex-row-reverse bg-body-secondary " 
                            key={video.MeetingID}
                        >
                            <button className="play-btn col-4" title={video.title} onClick={() => handleButtonClick(video.MeetingID, video.VideoURL)}>
                                <span role="img" aria-label="Play" style={{ fontSize: '3rem' }}>▶️</span>
                            </button>
                            <div className='col text-start'>
                                <h2 className="title">{video.Title}</h2>
                                <p>{video.Date}</p>
                                {/* <p className="description">{video.description}</p> */}
                                {/* <button className='btn btn-primary'>Watch</button> */}
                            </div>
                        </div>
                    ))
                    :
                    <p>No meetings available</p>
                :
                <LoadingSpinner />
                }
            </div>
        </div>
    )
}
