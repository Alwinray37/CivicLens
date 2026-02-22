// Catalog Page Component
// this will list the video as cards for users to click on and watch
// when clicked, it will take the user to the video watch page
import dummydata from '@assets/dummydata.json';
import styles from './CatalogPage.module.css';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import LoadingSpinner from '@components/icons/LoadingSpinner';

const CATALOG_ENDPOINT = `${window.location.origin}/api/getMeetings`;

export default function CatalogPage() {
    const [dateOrder, setDateOrder] = useState('desc');
    const [filterTag, setFilterTag] = useState('');
    const [search, setSearch] = useState('');

    const navigate = useNavigate();

    const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalogData });

    // debug: log query state so we can inspect fetched payload
    useEffect(() => {
        console.log('CatalogPage - catalogQuery state:', {
            isLoading: catalogQuery.isLoading,
            isError: catalogQuery.isError,
            data: catalogQuery.data,
            error: catalogQuery.error,
        });
    }, [catalogQuery.isLoading, catalogQuery.isError, catalogQuery.data, catalogQuery.error]);

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
            console.log('CatalogPage - fetchCatalogData response:', data);
            return data;
        } catch(err) {
            throw new Error(err);
        }
    }

    let filteredList = [];

    // Static list of tags related to civic meetings (used until API provides tags)
    const allTags = [
        "Budget",
        "Zoning",
        "Land Use",
        "Planning",
        "Transportation",
        "Public Works",
        "Parks & Recreation",
        "Housing",
        "Economic Development",
        "Public Safety",
        "Police",
        "Fire Department",
        "Environmental",
        "Utilities",
        "Education",
        "Procurement",
        "Ordinance",
        "Resolution",
        "Citizen Comments"
    ];

    if(catalogQuery.status === "success" && catalogQuery.data) {
        // Get the meetings array - could be catalogQuery.data.meetings or catalogQuery.data directly
        const meetingsData = catalogQuery.data.meetings || catalogQuery.data;
        
        if (!Array.isArray(meetingsData)) {
            console.error('Expected meetings array, got:', meetingsData);
            return;
        }
        
        // filter the data from dummydata, retrieve only the videos that have a videoUrl
        filteredList = meetingsData.filter(video => {
            if (video.VideoURL === null) return false;
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
            if (!a.Date || !b.Date) return 0;
            if (dateOrder === 'asc') {
                return new Date(a.Date) - new Date(b.Date);
            } else {
                return new Date(b.Date) - new Date(a.Date);
            }
        });


        // add thumbnail links to filteredList
        filteredList = filteredList.map(video => {
            const newVidObj = {...video};
            // create URL object to access search params easier
            const videoURL = new URL(newVidObj.VideoURL);
            // get 'v' search param, which is the YouTube video ID
            const ytVideoID = videoURL.searchParams.get('v');

            // construct thumbnail URL (high quality 720p)
            const thumbURL = `https://i.ytimg.com/vi/${ytVideoID}/hq720.jpg`;
            newVidObj['ThumbnailURL'] = thumbURL;

            return newVidObj;
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
                        <div className="video-card d-flex flex-row-reverse " 
                            key={video.MeetingID}
                        >
                            <button className={`col-4 ${styles.thumbnailBtn}`} title={video.title} onClick={() => handleButtonClick(video.MeetingID, video.VideoURL)}>
                                <img src={video.ThumbnailURL} />
                                <span className={`${styles.playIcon}`} role="img" aria-label="Play" >
                                    <i className="fa-solid fa-circle-play"></i>
                                </span>
                            </button>
                            <div className='col text-start d-flex flex-column justify-content-between'>
                                <div>
                                    <h2 className="title">{video.Title}</h2>
                                    <p>{video.Date}</p>
                                </div>
                                <div className="d-flex flex-wrap gap-1">
                                    <span className={`rounded p-1 px-2 text-dark ${styles.tag}`}>tag</span>
                                    <span className={`rounded p-1 px-2 text-dark ${styles.tag}`}>tag</span>
                                    <span className={`rounded p-1 px-2 text-dark ${styles.tag}`}>tag</span>
                                </div>
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
