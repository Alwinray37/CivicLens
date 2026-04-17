import { TAG_DEFINITIONS } from '@util/tagDefinitions';

export default function Header({ search, setSearch, selectedTags, setSelectedTags }) {
    const toggleTag = (tagId) => {
        setSelectedTags((currentTags) =>
            currentTags.includes(tagId)
                ? currentTags.filter((currentTag) => currentTag !== tagId)
                : [...currentTags, tagId]
        );
    };

    return (
        <div className="header d-flex flex-column align-items-center gap-3">
            {/* search bar */}
            <div className="search-bar-container">
                <input
                    type="text"
                    className="form-control"
                    placeholder="Search title..."
                    value={search}
                    onChange={e => setSearch(e.target.value)}
                />
            </div>

            {/* tags inline bar */}
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
