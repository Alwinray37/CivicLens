// Catalog Page Component
// Lists available meeting recordings and routes users to the watch page.
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import LoadingSpinner from '@components/icons/LoadingSpinner';
import { fetchCatalogData, getFilteredCatalogMeetings, getMeetingsFromCatalog } from '@util/catalog';

export default function CatalogPage() {
    const [dateOrder, setDateOrder] = useState('desc');
    const [search, setSearch] = useState('');

    const navigate = useNavigate();

    const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalogData });
    const meetings = catalogQuery.status === 'success' ? getMeetingsFromCatalog(catalogQuery.data) : [];
    const filteredList = getFilteredCatalogMeetings(meetings, search, dateOrder);


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
                        placeholder="Search title..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                        style={{ maxWidth: '180px' }}
                    />
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
                    <button className="btn btn-secondary" onClick={() => { setSearch(''); setDateOrder('desc'); }}>Clear</button>
                </div>
            </div>

            <div className="video-card-list container">
                {catalogQuery.isLoading ? (
                    <LoadingSpinner />
                ) : filteredList.length > 0 ? (
                    filteredList.map((video) => (
                        <div className="video-card d-flex flex-row-reverse " 
                            key={video.MeetingID}
                        >
                            <button className="col-4 catalog-thumbnail-btn" title={video.title} onClick={() => handleButtonClick(video.MeetingID, video.VideoURL)}>
                                <img src={video.ThumbnailURL} />
                                <span className="catalog-play-icon" role="img" aria-label="Play" >
                                    <i className="fa-solid fa-circle-play"></i>
                                </span>
                            </button>
                            <div className='col text-start d-flex flex-column justify-content-between'>
                                <div>
                                    <h2 className="title">{video.Title}</h2>
                                    <p>{video.Date}</p>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <p>No meetings available</p>
                )}
            </div>
        </div>
    )
}
