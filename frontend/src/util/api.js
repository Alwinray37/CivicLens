/**
 * Fetches JSON from an endpoint and validates the response shape at a basic level.
 * @param {string} endpoint - URL to request
 * @param {string} defaultErrorMessage - Message used when the request fails
 * @returns {Promise<any>} Parsed JSON payload
 * @throws {Error} If the request fails or the response is not JSON
 */
export async function fetchJson(endpoint, defaultErrorMessage = 'Server error') {
    try {
        const res = await fetch(endpoint);

        if (!res.ok) {
            throw new Error(defaultErrorMessage);
        }

        const contentType = res.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            const preview = (await res.text()).slice(0, 120);
            throw new Error(`Expected JSON response but got ${contentType || 'unknown content type'}: ${preview}`);
        }

        return await res.json();
    } catch (err) {
        throw new Error(err instanceof Error ? err.message : String(err));
    }
}
