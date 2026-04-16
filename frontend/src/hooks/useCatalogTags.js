import { useQueries } from '@tanstack/react-query';
import { fetchVideoData } from '@util/videoPageUtility';
import { inferTagsFromMeetingDetails } from '@util/tags';

export function useCatalogTags(meetings) {
    const tagQueries = useQueries({
        queries: meetings.map((meeting) => ({
            queryKey: ['videos', meeting.MeetingID],
            queryFn: () => fetchVideoData(meeting.MeetingID),
            staleTime: 5 * 60 * 1000,
            retry: 2,
            enabled: Boolean(meeting?.MeetingID),
        })),
    });

    return meetings.reduce((tagMap, meeting, index) => {
        const detailData = tagQueries[index]?.data;
        tagMap[meeting.MeetingID] = detailData ? inferTagsFromMeetingDetails(detailData) : [];
        return tagMap;
    }, {});
}
