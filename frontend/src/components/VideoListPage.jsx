// Video List Page Component
// this will list the video as cards for users to click on and watch
// when clicked, it will take the user to the video watch page
import dummydata from '../assets/dummydata.json';
import { useState } from 'react';

export default function VideoListPage() {
    const [dateOrder, setDateOrder] = useState('desc');
    const [filterTag, setFilterTag] = useState('');
    const [search, setSearch] = useState('');

    // Get all unique tags from the data
    const allTags = Array.from(new Set(dummydata.flatMap(video => video.tags || [])));

    let filteredList = dummydata.filter(video => {
        if (video.videoUrl === null) return false;
        const tagMatch = filterTag ? (video.tags || []).includes(filterTag) : true;
        // Search in title or tags
        const searchLower = search.toLowerCase();
        const titleMatch = video.title.toLowerCase().includes(searchLower);
        const tagsMatch = (video.tags || []).some(tag => tag.toLowerCase().includes(searchLower));
        const searchMatch = search ? (titleMatch || tagsMatch) : true;
        return tagMatch && searchMatch;
    });

    // Sort by date
    filteredList = filteredList.sort((a, b) => {
        if (!a.date || !b.date) return 0;
        if (dateOrder === 'asc') {
            return new Date(a.date) - new Date(b.date);
        } else {
            return new Date(b.date) - new Date(a.date);
        }
    });
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
                        <option value="">All Tags</option>
                        {allTags.map(tag => (
                            <option key={tag} value={tag}>{tag}</option>
                        ))}
                    </select>
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
                {filteredList.map((video) => (
                    <div className="video-card d-flex flex-row-reverse" key={video.id}>
                        <button className="play-btn col-4" title={video.title} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '2rem', width: '100px', height: '100px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <span role="img" aria-label="Play" style={{ fontSize: '3rem' }}>▶️</span>
                        </button>
                        <div className='col text-start'>
                            <h2 className="title">{video.title}</h2>
                            <p>{video.date}</p>
                            {/* <p className="description">{video.description}</p> */}
                            {/* <button className='btn btn-primary'>Watch</button> */}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}