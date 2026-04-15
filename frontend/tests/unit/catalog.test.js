import { describe, expect, test } from 'vitest';

import { buildThumbnailUrl, getFilteredCatalogMeetings, getMeetingsFromCatalog } from '../../src/util/catalog';

const meetings = [
    {
        MeetingID: 1,
        Title: 'Regular Meeting',
        Date: '2025-01-02',
        VideoURL: 'https://www.youtube.com/watch?v=abc123',
    },
    {
        MeetingID: 2,
        Title: 'Special Session',
        Date: '2025-01-01',
        VideoURL: 'https://www.youtube.com/watch?v=xyz789',
    },
    {
        MeetingID: 3,
        Title: 'Closed Session',
        Date: '2025-01-03',
        VideoURL: null,
    },
];

const tagsByMeetingId = {
    1: [{ id: 'budget', label: 'Budget' }],
    2: [{ id: 'housing', label: 'Housing' }],
    3: [],
};

describe('getMeetingsFromCatalog', () => {
    test('returns wrapped meetings arrays', () => {
        expect(getMeetingsFromCatalog({ meetings })).toEqual(meetings);
    });

    test('returns raw arrays unchanged', () => {
        expect(getMeetingsFromCatalog(meetings)).toEqual(meetings);
    });

    test('returns an empty array for invalid input', () => {
        expect(getMeetingsFromCatalog({ meetings: null })).toEqual([]);
        expect(getMeetingsFromCatalog(null)).toEqual([]);
    });
});

describe('buildThumbnailUrl', () => {
    test('returns a thumbnail url for valid YouTube links', () => {
        expect(buildThumbnailUrl('https://www.youtube.com/watch?v=abc123')).toBe('https://i.ytimg.com/vi/abc123/hq720.jpg');
    });

    test('returns null for invalid video urls', () => {
        expect(buildThumbnailUrl('not-a-url')).toBeNull();
        expect(buildThumbnailUrl('https://www.youtube.com/watch')).toBeNull();
    });
});

describe('getFilteredCatalogMeetings', () => {
    test('filters out meetings without a video url', () => {
        const result = getFilteredCatalogMeetings(meetings, '', 'desc', '', tagsByMeetingId);

        expect(result.map((meeting) => meeting.MeetingID)).toEqual([1, 2]);
    });

    test('filters meetings by search text', () => {
        const result = getFilteredCatalogMeetings(meetings, 'special', 'desc', '', tagsByMeetingId);

        expect(result).toHaveLength(1);
        expect(result[0].MeetingID).toBe(2);
    });

    test('filters meetings by selected tag', () => {
        const result = getFilteredCatalogMeetings(meetings, '', 'desc', 'budget', tagsByMeetingId);

        expect(result).toHaveLength(1);
        expect(result[0].MeetingID).toBe(1);
    });

    test('sorts meetings by date descending', () => {
        const result = getFilteredCatalogMeetings(meetings, '', 'desc', '', tagsByMeetingId);

        expect(result.map((meeting) => meeting.MeetingID)).toEqual([1, 2]);
    });

    test('sorts meetings by date ascending', () => {
        const result = getFilteredCatalogMeetings(meetings, '', 'asc', '', tagsByMeetingId);

        expect(result.map((meeting) => meeting.MeetingID)).toEqual([2, 1]);
    });

    test('adds thumbnail urls to filtered meetings', () => {
        const result = getFilteredCatalogMeetings(meetings, '', 'desc', '', tagsByMeetingId);

        expect(result[0].ThumbnailURL).toBe('https://i.ytimg.com/vi/abc123/hq720.jpg');
    });
});
