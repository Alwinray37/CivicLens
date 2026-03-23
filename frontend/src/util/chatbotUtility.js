const CHAT_ENDPOINT = '/api/chat'
const TOO_MANY_REQUESTS = 429;


export function createMessage(messageText, type) {
    const trimmedMessage = messageText.trim();
    if(trimmedMessage.length === 0) return null;

    return {
        message: trimmedMessage,
        type
    };
}

export async function fetchChatbot(query, meetingId) {
    if(query.length === 0) return;

    const res = await fetch(`${CHAT_ENDPOINT}/${meetingId}?query=${query}`);

    if(res.status === TOO_MANY_REQUESTS) {
        throw new Error("Chatbot is currently overloaded, try asking again in a minute");
    }

    if (!res.ok) {
        throw new Error("Server error");
    }

    const contentType = res.headers.get('content-type') || '';
    if (!contentType.includes('application/json')) {
        const preview = (await res.text()).slice(0, 120);
        throw new Error(`Expected JSON response but got ${contentType || 'unknown content type'}: ${preview}`);
    }

    const data = await res.json();

    if (!data) {
        throw new Error("Meeting does not have chat enabled");
    }

    return data;
}

