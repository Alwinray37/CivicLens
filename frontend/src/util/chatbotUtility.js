const CHAT_ENDPOINT = `${import.meta.env.BASE_URL}api/chat`
const TOO_MANY_REQUESTS = 429;

const QUESTION_TOO_LONG = 414;
const MAX_QUESTION_LEN = 300;


export function createMessage(type, messageText) {
    if(type === "pending") {
        messageText = "...";
    }

    const trimmedMessage = messageText.trim();
    if(trimmedMessage.length === 0) return null;

    return {
        message: trimmedMessage,
        type
    };
}

export async function fetchChatbot(query, meetingId) {
    const trimmedQuery = query.trim();
    if(trimmedQuery.length === 0) {
        throw new Error("Question cannot be empty.");
    }

    const res = await fetch(`${CHAT_ENDPOINT}/${meetingId}?query=${encodeURIComponent(trimmedQuery)}`);

    if(res.status === TOO_MANY_REQUESTS) {
        throw new Error("Chatbot is currently overloaded, try asking again in a minute.");
    }

    if(res.status === QUESTION_TOO_LONG) {
        throw new Error(`Question is too long. Reduce your question to a maximum of ${MAX_QUESTION_LEN} characters.`);
    }

    if (!res.ok) {
        throw new Error("Server error.");
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

