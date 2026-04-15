import { fetchJson } from '@util/api';

const CATALOG_ENDPOINT = `${import.meta.env.BASE_URL}api/getMeetings`;

/**
 * Fetches the meeting catalog from the API.
 * @returns {Promise<any>} Raw catalog payload
 */
export async function fetchCatalogData() {
    return fetchJson(CATALOG_ENDPOINT);
}

/**
 * Returns the array of meetings regardless of the API response wrapper shape.
 * @param {any} catalogData
 * @returns {Array}
 */
export function getMeetingsFromCatalog(catalogData) {
    const meetingsData = catalogData?.meetings || catalogData;
    return Array.isArray(meetingsData) ? meetingsData : [];
}

/**
 * Builds a YouTube thumbnail URL from a meeting video URL.
 * @param {string} videoUrl
 * @returns {string|null}
 */
export function buildThumbnailUrl(videoUrl) {
    if (!videoUrl) return null;

    try {
        const parsedUrl = new URL(videoUrl);
        const ytVideoId = parsedUrl.searchParams.get('v');

        if (!ytVideoId) return null;

        return `https://i.ytimg.com/vi/${ytVideoId}/hq720.jpg`;
    } catch {
        return null;
    }
}

/**
 * Filters, sorts, and decorates meeting rows for the catalog page.
 * @param {Array} meetings
 * @param {string} search
 * @param {'asc'|'desc'} dateOrder
 * @param {string} selectedTag
 * @param {Record<string|number, Array<{id: string, label: string}>>} tagsByMeetingId
 * @returns {Array}
 */
export function getFilteredCatalogMeetings(meetings, search, dateOrder, selectedTag = '', tagsByMeetingId = {}) {
    const searchLower = search.trim().toLowerCase();

    return meetings
        .filter((video) => {
            if (!video?.VideoURL) return false;

            const titleMatches = !searchLower || video.Title?.toLowerCase().includes(searchLower);
            const videoTags = tagsByMeetingId[video.MeetingID] || [];
            const tagMatches = !selectedTag || videoTags.some((tag) => tag.id === selectedTag);

            return titleMatches && tagMatches;
        })
        .sort((a, b) => {
            if (!a.Date || !b.Date) return 0;

            if (dateOrder === 'asc') {
                return new Date(a.Date) - new Date(b.Date);
            }

            return new Date(b.Date) - new Date(a.Date);
        })
        .map((video) => ({
            ...video,
            ThumbnailURL: buildThumbnailUrl(video.VideoURL),
        }));
}
