// Catalog Page Component
// this will list the video as cards for users to click on and watch
// when clicked, it will take the user to the video watch page
import dummydata from '@assets/dummydata.json';
import styles from './CatalogPage.module.css';
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import LoadingSpinner from '@components/icons/LoadingSpinner';

const CATALOG_ENDPOINT = '/api/getMeetings';

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

            const contentType = res.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
                const preview = (await res.text()).slice(0, 120);
                throw new Error(`Expected JSON response but got ${contentType || 'unknown content type'}: ${preview}`);
            }

            const data = await res.json();
            console.log('CatalogPage - fetchCatalogData response:', data);
            return data;
        } catch(err) {
            throw new Error(err instanceof Error ? err.message : String(err));
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

    const tagKeywordMap = {
        "Budget": ["budget", "finance", "fiscal", "appropriation"],
        "Zoning": ["zoning", "zone", "rezoning"],
        "Land Use": ["land use", "parcel", "site plan"],
        "Planning": ["planning", "master plan", "development plan"],
        "Transportation": ["transportation", "traffic", "transit", "road"],
        "Public Works": ["public works", "infrastructure", "maintenance"],
        "Parks & Recreation": ["park", "recreation", "trail"],
        "Housing": ["housing", "residential", "affordable housing"],
        "Economic Development": ["economic", "business", "downtown", "investment"],
        "Public Safety": ["public safety", "emergency", "safety"],
        "Police": ["police", "law enforcement"],
        "Fire Department": ["fire", "fire department"],
        "Environmental": ["environment", "sustainability", "climate", "air", "water"],
        "Utilities": ["utility", "utilities", "water", "sewer", "electric"],
        "Education": ["education", "school", "students"],
        "Procurement": ["procurement", "contract", "bid", "rfp"],
        "Ordinance": ["ordinance", "municipal code"],
        "Resolution": ["resolution"],
        "Citizen Comments": ["citizen comments", "public comment", "open forum"]
    };

    // Quick client-side tag extraction until backend tags are available.
    const getVideoTags = (video) => {
        const searchableContent = [video.Title, video.Description, video.Agenda]
            .filter(Boolean)
            .join(' ')
            .toLowerCase();

        const matchedTags = allTags.filter((tag) => {
            const keywords = tagKeywordMap[tag] || [];
            return keywords.some((keyword) => searchableContent.includes(keyword));
        });

        if (matchedTags.length >= 3) {
            return matchedTags.slice(0, 3);
        }

        // Deterministic per-video fallback so different cards get different tags.
        const seedSource = `${video.MeetingID || ''}-${video.Date || ''}-${video.Title || ''}`;
        const seed = seedSource.split('').reduce((acc, ch) => acc + ch.charCodeAt(0), 0);

        const tags = [...matchedTags];
        let offset = 0;
        while (tags.length < 3 && offset < allTags.length) {
            const nextTag = allTags[(seed + offset * 7) % allTags.length];
            if (!tags.includes(nextTag)) {
                tags.push(nextTag);
            }
            offset += 1;
        }

        return tags.slice(0, 3);
    };

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
            const videoTags = getVideoTags(video);
            const tagMatch = filterTag ? videoTags.includes(filterTag) : true;
            // Search in title or tags
            const searchLower = search.toLowerCase();
            const titleMatch = video.Title.toLowerCase().includes(searchLower);
            const tagsMatch = videoTags.some(tag => tag.toLowerCase().includes(searchLower));
            const searchMatch = search ? (titleMatch || tagsMatch) : true;
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
            newVidObj.tags = getVideoTags(newVidObj);
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
                            <button className={`col-4 ${styles.thumbnailBtn}`} title={video.Title} onClick={() => handleButtonClick(video.MeetingID, video.VideoURL)}>
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
                                    {(video.tags || []).map((tag) => (
                                        <span key={`${video.MeetingID}-${tag}`} className={`rounded p-1 px-2 text-dark ${styles.tag}`}>{tag}</span>
                                    ))}
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
