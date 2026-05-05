import { useEffect, useState } from "react";
import { useMutation, useQuery } from '@tanstack/react-query';
import { createMessage, fetchChatbot, fetchChatHistory } from "@/util/chatbotUtility";

export function useChatbot(meetingId, clearInputFunc) {
    const historyQuery = useQuery({ 
        queryKey: ['chatHistory'], 
        queryFn: () => fetchChatHistory(meetingId),

        // TODO: consider including ttl for chat messages in response, use this to determine staleTime
        staleTime: 0, // chat history ttl in frontend currently not known
        gcTime: 0,

        refetchOnWindowFocus: false,

        retry: 2, // Retry failed requests twice
    });

    const chatQuery = useMutation({
        mutationKey: [meetingId],
        mutationFn: (query) => fetchChatbot(query, meetingId),
        onMutate: (query) => handleMutation(query),
        onSuccess: (answer) => handleResponse("incoming", answer.Response),
        onError: (error) => handleResponse("error", error.message),
        retry: 0,
    });

    /* 
        * messages: {
            * type: "outgoing" | "incoming" | "error" | "pending"
                * outgoing messages appear on right, others appear on left
            * message: string
        * }[]
    */
    const [messages, setMessages] = useState([]);


    useEffect(() => {
        // prepend chat history if there's a successful fetch
        if(historyQuery.isSuccess) {
            const chatHistory = historyQuery.data.ChatHistory.map(cr => ({ type: cr.Type, message: cr.Response }));
            setMessages((cur) => [...chatHistory, ...cur]);
        }
    }, [historyQuery.isSuccess]);

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
