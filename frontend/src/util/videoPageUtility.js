import { fetchJson } from '@util/api';

/**
 * Fetches video meeting data from the API
 * @param {string|number} id - The meeting ID
 * @returns {Promise<Object>} Meeting data including video info, summaries, agenda, etc.
 * @throws {Error} If the request fails or meeting is not found
 */
export async function fetchVideoData(id) {
    const data = await fetchJson(`${import.meta.env.BASE_URL}api/getMeetingInfo/${id}`);

    if (!data) {
        throw new Error("Meeting not found");
    }

    return data;
}

/**
 * Configuration for ReactPlayer
 */
export const PLAYER_CONFIG = {
    youtube: {
        playerVars: { 
            modestbranding: 1, 
            rel: 0, 
            showinfo: 0 
        },
    },
};

/**
 * Style configuration for ReactPlayer
 */
export const PLAYER_STYLE = {
    minWidth: "300px",
    width: "100%",
    height: "auto",
    aspectRatio: "16 / 9",
};
