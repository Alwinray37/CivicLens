// Catalog Page Component
// Lists available meeting recordings and routes users to the watch page.
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import LoadingSpinner from '@components/icons/LoadingSpinner';
import { useCatalogMeetingDetails } from '@hooks/useCatalogTags';
import { fetchCatalogData, getFilteredCatalogMeetings, getMeetingsFromCatalog } from '@util/catalog';
import Header from '@components/Header';
import IntoSection from '@components/IntoSection';

function getSummarySubtitle(summaries) {
    const summaryTitles = summaries
        .slice(0, 3)
        .map((summary) => summary?.Title?.trim())
        .filter(Boolean);

    return summaryTitles.length > 0 ? summaryTitles.join(' * ') : '';
}

function getSummaryPreview(summaries) {
    const summaryBodies = summaries
        .slice(0, 3)
        .map((summary) => summary?.Summary?.trim())
        .filter(Boolean);

    return summaryBodies.length > 0 ? summaryBodies.join(' ') : 'No summary available';
}

export default function CatalogPage() {
    const [dateOrder, setDateOrder] = useState('desc');
    const [search, setSearch] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);

    const navigate = useNavigate();

    const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalogData });
    const meetings = catalogQuery.status === 'success' ? getMeetingsFromCatalog(catalogQuery.data) : [];
    const { tagsByMeetingId, summariesByMeetingId } = useCatalogMeetingDetails(meetings);
    const filteredList = getFilteredCatalogMeetings(meetings, search, dateOrder, selectedTags, tagsByMeetingId);


    // handle button click to open video page 
    // navigates to /watch/:id route with videoId as param
    const handleButtonClick = (videoId, videoUrl) => {
        navigate (`/watch/${videoId}`, { state: { videoId, videoUrl } });
    };

    const scrollToFilters = () => {
        document.getElementById('meeting-filters')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    return (
        <div className="container" id="video-list-page">
            <IntoSection onBrowseMeetings={scrollToFilters} />

            <Header
                sectionId="meeting-filters"
                search={search}
                setSearch={setSearch}
                dateOrder={dateOrder}
                setDateOrder={setDateOrder}
                selectedTags={selectedTags}
                setSelectedTags={setSelectedTags}
            />
            <div className="heading d-flex align-items-center justify-content-center p-4">
                <h1>Civic Meetings</h1>
            </div>

            <div className="video-card-list container" id="meeting-results">
                {catalogQuery.isLoading ? (
                    <LoadingSpinner />
                ) : filteredList.length > 0 ? (
                    filteredList.map((video) => {
                        const videoTags = tagsByMeetingId[video.MeetingID] || [];
                        const videoSummaries = summariesByMeetingId[video.MeetingID] || [];
                        const summarySubtitle = getSummarySubtitle(videoSummaries);
                        const summaryPreview = getSummaryPreview(videoSummaries);

                        return (
                            <div
                                className="video-card catalog-video-card"
                                key={video.MeetingID}
                                onClick={() => handleButtonClick(video.MeetingID, video.VideoURL)}
                            >
                                <div className="catalog-video-card-layout">
                                    <div className="catalog-thumbnail" title={video.Title}>
                                        <img src={video.ThumbnailURL} alt={video.Title} />
                                        <span className="catalog-play-icon" role="img" aria-label="Play" >
                                            <i className="fa-solid fa-circle-play"></i>
                                        </span>
                                    </div>

                                    <div className="catalog-summary-preview d-none d-lg-flex">
                                        <p className="catalog-summary-preview-text mb-0">
                                            {summaryPreview}
                                        </p>
                                    </div>

                                    <div className="catalog-video-meta text-start d-flex flex-column justify-content-between">
                                        <div>
                                            <h2 className="title mb-2">{video.Title}</h2>
                                            {summarySubtitle && (
                                                <p className="catalog-video-subtitle d-none d-lg-block">
                                                    {summarySubtitle}
                                                </p>
                                            )}
                                            <p className="catalog-video-date">
                                                {video.Date ? new Date(video.Date).toLocaleDateString("en-US", {
                                                        year: "numeric",
                                                        month: "long",
                                                        day: "numeric",
                                                    }) : 'No date available'
                                                }
                                            </p>
                                            {videoTags.length > 0 && (
                                                <div className="catalog-tag-list d-flex flex-wrap gap-2 mt-3">
                                                    {videoTags.map((tag) => (
                                                        <span key={tag.id} className="catalog-tag">
                                                            {tag.label}
                                                        </span>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        );
                    })
                ) : (
                    <h2>No meetings available</h2>
                )}
            </div>
        </div>
    )
}
