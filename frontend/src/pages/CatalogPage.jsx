// Catalog Page Component
// Lists available meeting recordings and routes users to the watch page.
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import LoadingSpinner from '@components/icons/LoadingSpinner';
import { useCatalogTags } from '@hooks/useCatalogTags';
import { fetchCatalogData, getFilteredCatalogMeetings, getMeetingsFromCatalog } from '@util/catalog';
import Header from '@components/Header';

export default function CatalogPage() {
    const [dateOrder, setDateOrder] = useState('desc');
    const [search, setSearch] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);

    const navigate = useNavigate();

    const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalogData });
    const meetings = catalogQuery.status === 'success' ? getMeetingsFromCatalog(catalogQuery.data) : [];
    const tagsByMeetingId = useCatalogTags(meetings);
    const filteredList = getFilteredCatalogMeetings(meetings, search, dateOrder, selectedTags, tagsByMeetingId);


    // handle button click to open video page 
    // navigates to /watch/:id route with videoId as param
    const handleButtonClick = (videoId, videoUrl) => {
        navigate (`/watch/${videoId}`, { state: { videoId, videoUrl } });
    }

    return (
        <div className="container" id="video-list-page">
            <Header
                search={search}
                setSearch={setSearch}
                selectedTags={selectedTags}
                setSelectedTags={setSelectedTags}
            />
            <div className="heading d-flex align-items-center justify-content-between">
                <h1>Civic Meetings</h1>

                {/* search and filter component */}
                <div className="filter d-flex gap-2">
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
                    {/* tags */}
                    <button className="btn btn-secondary" onClick={() => { setSearch(''); setDateOrder('desc'); setSelectedTags([]); }}>Clear</button>
                </div>
            </div>

            <div className="video-card-list container">
                {catalogQuery.isLoading ? (
                    <LoadingSpinner />
                ) : filteredList.length > 0 ? (
                    filteredList.map((video) => (
                        // video card component - displays video thumbnail, title, date, and tags
                        <div className="video-card d-flex flex-row-reverse " 
                            key={video.MeetingID}
                            onClick={() => handleButtonClick(video.MeetingID, video.VideoURL)}
                        >
                            <div className="col-4 catalog-thumbnail" title={video.title}>
                                <img src={video.ThumbnailURL} />
                                <span className="catalog-play-icon" role="img" aria-label="Play" >
                                    <i className="fa-solid fa-circle-play"></i>
                                </span>
                            </div>
                            <div className='col text-start d-flex flex-column justify-content-between'>
                                <div>
                                    <h2 className="title">{video.Title}</h2>
                                    <p>{video.Date ? new Date(video.Date).toLocaleDateString("en-US", {
                                            year: "numeric",
                                            month: "long",
                                            day: "numeric",
                                            }) : 'No date available'
                                }
                                    </p>
                                    {tagsByMeetingId[video.MeetingID]?.length > 0 && (
                                        <div className="catalog-tag-list d-flex flex-wrap gap-2 mt-3">
                                            {tagsByMeetingId[video.MeetingID].map((tag) => (
                                                <span key={tag.id} className="catalog-tag">
                                                    {tag.label}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <h2>No meetings available</h2>
                )}
            </div>
        </div>
    )
}
