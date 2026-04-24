import { useQueries } from '@tanstack/react-query';
import { fetchVideoData } from '@util/videoPageUtility';
import { inferTagsFromMeetingDetails } from '@util/tags';

function sortSummariesByStartTime(summaries) {
    return Array.isArray(summaries)
        ? [...summaries].sort((a, b) => (a?.StartTime || '').localeCompare(b?.StartTime || ''))
        : [];
}

export function useCatalogMeetingDetails(meetings) {
    const detailQueries = useQueries({
        queries: meetings.map((meeting) => ({
            queryKey: ['videos', meeting.MeetingID],
            queryFn: () => fetchVideoData(meeting.MeetingID),
            staleTime: 5 * 60 * 1000,
            retry: 2,
            enabled: Boolean(meeting?.MeetingID),
        })),
    });

    return meetings.reduce((catalogDetails, meeting, index) => {
        const detailQuery = detailQueries[index];
        const detailData = detailQuery?.data;

        catalogDetails.tagsByMeetingId[meeting.MeetingID] = detailData
            ? inferTagsFromMeetingDetails(detailData)
            : [];
        catalogDetails.summariesByMeetingId[meeting.MeetingID] = sortSummariesByStartTime(detailData?.summaries);
        catalogDetails.detailStatusByMeetingId[meeting.MeetingID] = {
            isPending: detailQuery?.status === 'pending',
            isSuccess: detailQuery?.status === 'success',
            isError: detailQuery?.status === 'error',
        };

        return catalogDetails;
    }, {
        detailStatusByMeetingId: {},
        tagsByMeetingId: {},
        summariesByMeetingId: {},
    });
}

export function useCatalogTags(meetings) {
    return useCatalogMeetingDetails(meetings).tagsByMeetingId;
}
