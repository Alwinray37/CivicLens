import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import LoadingSpinner from '@components/icons/LoadingSpinner';
import { useCatalogMeetingDetails } from '@hooks/useCatalogTags';
import {
    fetchCatalogData,
    formatCatalogMeetingDate,
    getFilteredCatalogMeetings,
    getMeetingsFromCatalog,
} from '@util/catalog';
import Header from '@components/Header';
import IntroSection from '@components/IntroSection';

function getSummarySubtitle(summaries) {
    const summaryTitles = summaries
        .slice(0, 2)
        .map((summary) => summary?.Title?.trim())
        .filter(Boolean);

    return summaryTitles.length > 0 ? summaryTitles.join(' • ') : '';
}

function getCatalogTopicLine(summaries, detailsLoaded) {
    if (!detailsLoaded) return '';
    if (summaries.length === 0) return 'No summary available';

    return getSummarySubtitle(summaries);
}

export function CatalogMeetingCard({
    video,
    videoTags = [],
    videoSummaries = [],
    detailsLoaded = false,
    onOpen,
}) {
    const summarySubtitle = getCatalogTopicLine(videoSummaries, detailsLoaded);

    const handleKeyDown = (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            onOpen(video.MeetingID, video.VideoURL);
        }
    };

    return (
        <div
            className="video-card catalog-video-card"
            role="button"
            tabIndex={0}
            onClick={() => onOpen(video.MeetingID, video.VideoURL)}
            onKeyDown={handleKeyDown}
        >
            <div className="catalog-video-card-layout">
                <div className="catalog-thumbnail" title={video.Title}>
                    {video.ThumbnailURL ? (
                        <img src={video.ThumbnailURL} alt={video.Title} />
                    ) : (
                        <div className="catalog-thumbnail-fallback" aria-hidden="true">
                            No preview
                        </div>
                    )}
                    <span className="catalog-play-icon" aria-hidden="true">
                        <i className="fa-solid fa-circle-play"></i>
                    </span>
                </div>

                <div className="catalog-video-meta text-start">
                    <div className="catalog-video-copy">
                        <p className="catalog-video-date">
                            {formatCatalogMeetingDate(video.Date)}
                        </p>
                        <h2 className="title catalog-video-title mb-0">{video.Title}</h2>
                        {summarySubtitle && (
                            <p className="catalog-video-subtitle mb-0">
                                {summarySubtitle}
                            </p>
                        )}
                    </div>

                    <div className="catalog-card-footer">
                        {videoTags.length > 0 && (
                            <div className="catalog-tag-list d-flex flex-wrap gap-2">
                                {videoTags.map((tag) => (
                                    <span key={tag.id} className="catalog-tag">
                                        {tag.label}
                                    </span>
                                ))}
                            </div>
                        )}

                        <span className="catalog-watch-cue">
                            <i className="fa-solid fa-circle-play" aria-hidden="true"></i>
                            Watch meeting
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default function CatalogPage() {
    const [dateOrder, setDateOrder] = useState('desc');
    const [search, setSearch] = useState('');
    const [selectedTags, setSelectedTags] = useState([]);

    const navigate = useNavigate();

    const catalogQuery = useQuery({ queryKey: ['catalog'], queryFn: fetchCatalogData });
    const meetings = catalogQuery.status === 'success' ? getMeetingsFromCatalog(catalogQuery.data) : [];
    const { tagsByMeetingId, summariesByMeetingId, detailStatusByMeetingId } = useCatalogMeetingDetails(meetings);
    const filteredList = getFilteredCatalogMeetings(
        meetings,
        search,
        dateOrder,
        selectedTags,
        tagsByMeetingId,
        summariesByMeetingId
    );


    const handleButtonClick = (videoId, videoUrl) => {
        navigate (`/watch/${videoId}`, { state: { videoId, videoUrl } });
    };

    const scrollToFilters = () => {
        document.getElementById('meeting-filters')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };

    return (
        <div className="container" id="video-list-page">
            <IntroSection onBrowseMeetings={scrollToFilters} />

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
                        const detailsLoaded = detailStatusByMeetingId[video.MeetingID]?.isSuccess;

                        return (
                            <CatalogMeetingCard
                                key={video.MeetingID}
                                video={video}
                                videoTags={videoTags}
                                videoSummaries={videoSummaries}
                                detailsLoaded={detailsLoaded}
                                onOpen={handleButtonClick}
                            />
                        );
                    })
                ) : (
                    <h2>No meetings available</h2>
                )}
            </div>
        </div>
    )
}
