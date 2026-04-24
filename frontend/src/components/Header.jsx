import { TAG_DEFINITIONS } from '@util/tagDefinitions';

export default function Header({
    sectionId,
    search,
    setSearch,
    dateOrder,
    setDateOrder,
    selectedTags,
    setSelectedTags,
}) {
    const toggleTag = (tagId) => {
        setSelectedTags((currentTags) =>
            currentTags.includes(tagId)
                ? currentTags.filter((currentTag) => currentTag !== tagId)
                : [...currentTags, tagId]
        );
    };

    const clearFilters = () => {
        setSearch('');
        setDateOrder('desc');
        setSelectedTags([]);
    };

    return (
        <div className="header d-flex flex-column align-items-center gap-3" id={sectionId}>
            <div className="header-controls d-flex flex-wrap justify-content-center gap-2">
                <div className="search-bar-container">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search title..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </div>

                <select
                    className="form-select header-sort-select"
                    value={dateOrder}
                    onChange={e => setDateOrder(e.target.value)}
                    aria-label="Sort meetings by date"
                >
                    <option value="desc">Newest First</option>
                    <option value="asc">Oldest First</option>
                </select>

                <button type="button" className="btn btn-secondary" onClick={clearFilters}>
                    Clear
                </button>
            </div>

            <div className="tags-container d-flex gap-2 flex-wrap justify-content-center">
                {TAG_DEFINITIONS.map((tag) => {
                    const isActive = selectedTags.includes(tag.id);

                    return (
                        <button
                            key={tag.id}
                            type="button"
                            className={`tag-btn ${isActive ? 'active' : ''}`}
                            onClick={() => toggleTag(tag.id)}
                            aria-pressed={isActive}
                        >
                            {tag.label}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}
