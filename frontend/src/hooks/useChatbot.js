import { useEffect, useState } from "react";
import { useMutation } from '@tanstack/react-query';
import { createMessage, fetchChatbot } from "@/util/chatbotUtility";

export function useChatbot(meetingId, clearInputFunc, chatHistory) {
    /* 
        * messages: {
            * type: "outgoing" | "incoming" | "error" | "pending"
                * outgoing messages appear on right, others appear on left
            * message: string
        * }[]
    */
    const [messages, setMessages] = useState(chatHistory);

    const chatQuery = useMutation({
        mutationKey: [meetingId],
        mutationFn: (query) => fetchChatbot(query, meetingId),
        onMutate: (query) => handleMutation(query),
        onSuccess: (answer) => handleResponse("incoming", answer.Response),
        onError: (error) => handleResponse("error", error.message),
        retry: 0,
    });

    useEffect(() => {
        const loadingMessageIndex = messages.findIndex((m) => m.type === "pending");

        if (!chatQuery.isPending) {
            if (loadingMessageIndex === -1) return;

            setMessages((cur) => [
                ...cur.slice(0, loadingMessageIndex),
                ...cur.slice(loadingMessageIndex + 1),
            ]);
            return;
        }

        if (loadingMessageIndex === -1) {
            const pendingMessage = createMessage("pending");
            if (pendingMessage) {
                setMessages((cur) => [...cur, pendingMessage]);
            }
            return;
        }

        if (loadingMessageIndex !== messages.length - 1) {
            setMessages((cur) => [
                ...cur.slice(0, loadingMessageIndex),
                ...cur.slice(loadingMessageIndex + 1),
                cur[loadingMessageIndex],
            ]);
        }
    }, [chatQuery.isPending, messages]);

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

    return [ messages, sendMessage ];
}
