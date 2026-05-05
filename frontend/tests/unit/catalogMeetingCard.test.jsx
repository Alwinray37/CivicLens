import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, test } from 'vitest';

import { CatalogMeetingCard } from '../../src/pages/CatalogPage.jsx';

const baseVideo = {
    MeetingID: 1,
    Title: 'Regular Council Meeting',
    Date: '2025-01-02',
    VideoURL: 'https://www.youtube.com/watch?v=abc123',
    ThumbnailURL: 'https://i.ytimg.com/vi/abc123/hq720.jpg',
};

function renderCard(props = {}) {
    return renderToStaticMarkup(
        <CatalogMeetingCard
            video={props.video || baseVideo}
            videoTags={props.videoTags || []}
            videoSummaries={props.videoSummaries || []}
            detailsLoaded={props.detailsLoaded ?? true}
            onOpen={() => {}}
        />,
    );
}

describe('CatalogMeetingCard', () => {
    test('renders provided tags directly without an overflow badge', () => {
        const html = renderCard({
            videoTags: [
                { id: 'budget', label: 'Budget' },
                { id: 'housing', label: 'Housing' },
                { id: 'transportation', label: 'Transportation' },
                { id: 'parks', label: 'Parks & Rec' },
            ],
        });

        expect(html).toContain('Budget');
        expect(html).toContain('Housing');
        expect(html).toContain('Transportation');
        expect(html).toContain('Parks &amp; Rec');
        expect(html).not.toContain('>+1<');
    });

    test('shows no-summary fallback only when details loaded with zero summaries', () => {
        expect(renderCard({ videoSummaries: [], detailsLoaded: true })).toContain('No summary available');
        expect(renderCard({ videoSummaries: [], detailsLoaded: false })).not.toContain('No summary available');
    });

    test('does not render summary bodies or false fallback when summary titles are missing', () => {
        const html = renderCard({
            videoSummaries: [{ Summary: 'This long summary body should stay off the catalog card.' }],
        });

        expect(html).not.toContain('This long summary body should stay off the catalog card.');
        expect(html).not.toContain('No summary available');
    });

    test('renders missing-thumbnail fallback and watch cue', () => {
        const html = renderCard({
            video: {
                ...baseVideo,
                ThumbnailURL: null,
            },
        });

        expect(html).toContain('No preview');
        expect(html).toContain('Watch meeting');
    });
});
