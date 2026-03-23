import { useState } from "react";
import { useMutation } from '@tanstack/react-query';
import { createMessage, fetchChatbot } from "@/util/chatbotUtility";

export function useChatbot(meetingId, clearInputFunc) {
    /* 
        * messages: {
            * type: "outgoing" | "incoming" | "error"
                * outgoing messages appear on right, others appear on left
            * message: string
        * }[]
    */
    const [messages, setMessages] = useState([]);
    const chatQuery = useMutation({
        mutationKey: [meetingId],
        mutationFn: (query) => fetchChatbot(query, meetingId),
        onMutate: (query) => appendMessage(createMessage(query, "outgoing")),
        onSuccess: (answer) => appendMessage(createMessage(answer.Response, "incoming")),
        onError: (error) => appendMessage(createMessage(error.message, "error")),
        retry: 0,
    });

    function sendMessage(messageText) {
        chatQuery.mutate(messageText);
    }

    // appends a message to the chatbot
    function appendMessage(message) {
        if(message === null) return;
        setMessages((curMessages) => [...curMessages, message]);


        if(message.type === "outgoing") clearInputFunc();
    }

    return [ messages, sendMessage ];
}
