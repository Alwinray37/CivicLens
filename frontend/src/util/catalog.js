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
 * Formats a meeting date for consistent display and search matching.
 * Handles date-only strings without shifting the day across time zones.
 * @param {string} dateValue
 * @returns {string}
 */
export function formatCatalogMeetingDate(dateValue) {
    if (!dateValue) return 'No date available';

    let parsedDate;

    if (/^\d{4}-\d{2}-\d{2}$/.test(dateValue)) {
        const [year, month, day] = dateValue.split('-').map(Number);
        parsedDate = new Date(Date.UTC(year, month - 1, day));
    } else {
        parsedDate = new Date(dateValue);
    }

    if (Number.isNaN(parsedDate.getTime())) {
        return 'No date available';
    }

    return parsedDate.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        timeZone: 'UTC',
    });
}

/**
 * Filters, sorts, and decorates meeting rows for the catalog page.
 * @param {Array} meetings
 * @param {string} search
 * @param {'asc'|'desc'} dateOrder
 * @param {string[]} selectedTags
 * @param {Record<string|number, Array<{id: string, label: string}>>} tagsByMeetingId
 * @param {Record<string|number, Array<{Title?: string, Summary?: string}>>} summariesByMeetingId
 * @returns {Array}
 */
export function getFilteredCatalogMeetings(
    meetings,
    search,
    dateOrder,
    selectedTags = [],
    tagsByMeetingId = {},
    summariesByMeetingId = {}
) {
    const searchLower = search.trim().toLowerCase();
    const selectedTagSet = new Set(selectedTags);

    return meetings
        .filter((video) => {
            if (!video?.VideoURL) return false;

            const videoTags = tagsByMeetingId[video.MeetingID] || [];
            const videoSummaries = summariesByMeetingId[video.MeetingID] || [];
            const formattedDate = video.Date ? formatCatalogMeetingDate(video.Date).toLowerCase() : '';
            const searchableSubtitle = videoSummaries
                .map((summary) => summary?.Title?.trim())
                .filter(Boolean)
                .join(' ')
                .toLowerCase();
            const searchableTags = videoTags
                .map((tag) => `${tag.id} ${tag.label}`.trim())
                .join(' ')
                .toLowerCase();
            const searchableTitle = video.Title?.toLowerCase() || '';
            const searchMatches = !searchLower || [
                searchableTitle,
                searchableSubtitle,
                searchableTags,
                formattedDate,
            ].some((value) => value.includes(searchLower));
            const tagMatches = selectedTagSet.size === 0 || videoTags.some((tag) => selectedTagSet.has(tag.id));

            return searchMatches && tagMatches;
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
