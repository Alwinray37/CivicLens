import { useState } from "react";
import { useMutation } from '@tanstack/react-query';
import { createMessage, fetchChatbot } from "@/util/chatbotUtility";

export function useChatbot(meetingId, clearInputFunc) {
    /* 
        * messages: {
            * type: "outgoing" | "incoming" | "error" | "pending"
                * outgoing messages appear on right, others appear on left
            * message: string
        * }[]
    */
    const [messages, setMessages] = useState([]);

    const chatQuery = useMutation({
        mutationKey: [meetingId],
        mutationFn: (query) => fetchChatbot(query, meetingId),
        onMutate: (query) => handleMutation(query),
        onSuccess: (answer) => handleResponse("incoming", answer.Response),
        onError: (error) => handleResponse("error", error.message),
        retry: 0,
    });

    handleLoadingState();

    function handleMutation(query) {
        appendMessage(createMessage("outgoing", query));
    }

    function handleResponse(type, responseText) {
        const response = createMessage(type, responseText);

        appendMessage(response);
    }

    function sendMessage(messageText) {
        chatQuery.mutate(messageText);
    }

    // appends a message to the chatbot
    function appendMessage(message) {
        if(message === null) return;

        setMessages(curMessages => [...curMessages, message]);

        if(message.type === "outgoing") clearInputFunc();
    }

    function handleLoadingState() {
        const loadingMessageIndex = messages.findIndex((m) => m.type === "pending");

        if(!chatQuery.isPending) {
            if(loadingMessageIndex === -1) return;

            setMessages(cur => [
                            ...cur.slice(0, loadingMessageIndex),
                            ...cur.slice(loadingMessageIndex + 1),
                        ]);
        } else if(loadingMessageIndex === -1) {
            appendMessage(createMessage("pending"));
        } else if(loadingMessageIndex !== messages.length - 1) {
            setMessages(cur => [
                ...cur.slice(0, loadingMessageIndex),
                ...cur.slice(loadingMessageIndex + 1),
                messages[loadingMessageIndex],
            ]);
        }
    }

    return [ messages, sendMessage ];
}
