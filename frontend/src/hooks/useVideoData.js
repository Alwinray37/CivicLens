import { useQuery } from "@tanstack/react-query";
import { fetchVideoData } from "@util/videoPageUtility";

/**
 * Custom hook to fetch video meeting data
 * @param {string|number} id - The meeting ID
 * @returns {Object} React Query result object
 */
export function useVideoData(id) {
    return useQuery({ 
        queryKey: ['videos', id], 
        queryFn: () => fetchVideoData(id),
        staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
        retry: 2, // Retry failed requests twice
    });
}
