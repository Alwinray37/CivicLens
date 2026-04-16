import { afterEach, describe, expect, test, vi } from 'vitest';

import { fetchVideoData, PLAYER_CONFIG, PLAYER_STYLE } from '../../src/util/videoPageUtility';

function mockFetchResponse({
    ok = true,
    contentType = 'application/json',
    jsonData = null,
    textData = '',
} = {}) {
    return {
        ok,
        headers: {
            get: (header) => header === 'content-type' ? contentType : null,
        },
        json: vi.fn().mockResolvedValue(jsonData),
        text: vi.fn().mockResolvedValue(textData),
    };
}

afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
});

describe('fetchVideoData', () => {
    test('returns meeting detail data for a valid JSON response', async () => {
        const mockData = {
            meeting: {
                MeetingID: 4,
                Title: 'Regular Meeting',
                Date: '2025-01-01',
                VideoURL: 'https://www.youtube.com/watch?v=abc123',
            },
            agenda: [],
            summaries: [],
        };

        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockFetchResponse({ jsonData: mockData })));

        const data = await fetchVideoData(4);

        expect(fetch).toHaveBeenCalledWith('/api/getMeetingInfo/4');
        expect(data).toEqual(mockData);
    });

    test('throws a server error when the response is not ok', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockFetchResponse({ ok: false })));

        await expect(fetchVideoData(4)).rejects.toThrow('Server error');
    });

    test('throws when the response content type is not JSON', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(
            mockFetchResponse({
                contentType: 'text/html',
                textData: '<html>not json</html>',
            }),
        ));

        await expect(fetchVideoData(4)).rejects.toThrow('Expected JSON response');
    });

    test('throws when no meeting data is returned', async () => {
        vi.stubGlobal('fetch', vi.fn().mockResolvedValue(mockFetchResponse({ jsonData: null })));

        await expect(fetchVideoData(4)).rejects.toThrow('Meeting not found');
    });

    test('surfaces fetch failures', async () => {
        vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network down')));

        await expect(fetchVideoData(4)).rejects.toThrow('Network down');
    });
});

describe('PLAYER_CONFIG', () => {
    test('sets the expected YouTube player options', () => {
        expect(PLAYER_CONFIG.youtube.playerVars).toMatchObject({
            modestbranding: 1,
            rel: 0,
            showinfo: 0,
        });
    });
});

describe('PLAYER_STYLE', () => {
    test('exports responsive player dimensions', () => {
        expect(PLAYER_STYLE).toMatchObject({
            minWidth: '300px',
            width: '100%',
            height: 'auto',
            aspectRatio: '16 / 9',
        });
    });
});
