import { useEffect, useRef, useState } from 'react';
import styles from './Chatbot.module.css';

import ChatbotMessage from './ChatbotMessage';
import { useMutation } from '@tanstack/react-query';

const CHAT_ENDPOINT = '/api/chat'

export default function Chatbot({
    meetingId,
}) {
    /* 
        * messages: {
            * type: "outgoing" | "incoming"
                * outgoing messages appear on right, outgoing appear on left
            * message: string
        * }[]
    */
    const [messages, setMessages] = useState([]);
    const [messageInput, setMessageInput] = useState("");
    const chatQuery = useMutation({
        mutationKey: [meetingId],
        mutationFn: fetchChatbot,
        onMutate: (query) => sendMessage(query, "outgoing"),
        onSuccess: (answer) => sendMessage(answer.Response, "incoming"),
        retry: 2,
    });

    async function fetchChatbot(query) {
        const res = await fetch(`${CHAT_ENDPOINT}/${meetingId}?query=${query}`);

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

    // ref of the div the contains the messages
    const messageContainerRef = useRef(null);

    // scrolls to bottom of messages
    const scrollToBottom = () => {
        messageContainerRef.current?.scroll({
            behavior: "instant",
            top: messageContainerRef.current.scrollHeight,
        })
    }

    // sends a message to the chatbot
    const sendMessage = (message, type) => {
        const trimmedMessage = message.trim();
        if(trimmedMessage.length === 0) return;

        setMessages((curMessages) => [...curMessages, {
            type,
            message: trimmedMessage,
        }]);


        if(type === "outgoing") setMessageInput("");
        
        scrollToBottom();
    }

    // handles user keystrokes in the chatbot input field
    const handleMessageKeyDown = (e) => {
        if(e.key === "Enter") {
            chatQuery.mutate(messageInput);
        }
    }

    // updates state of user input
    const handleMessageChange = (e) => {
        setMessageInput(e.target.value);
    }

    // scrolls to bottom of chatbox whenever messages is updated
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className={"container rounded text-start p-0 h-100 d-flex flex-column justify-content-between bg-body-secondary "
                        + styles.chatbotWrapper}>
            <h4 className="border-bottom py-2 mx-2 mb-0 ps-1 pb-2 text-body-secondary fw-bold">Chatbot</h4>
            <div 
                className="d-flex flex-column flex-grow-1 overflow-y-scroll min-scrollbar my-1 text-body-secondary"
                ref={messageContainerRef}
            >
                {
                messages.length > 0 ?
                    messages.map((m, i) =>
                        <ChatbotMessage message={m.message} type={m.type} key={i}/>
                    )
                :
                    <div className="h-100 d-flex align-items-center justify-content-center text-body-tertiary">
                        <span>
                            Ask a question about the video
                        </span>
                    </div>
                }
            </div>
            <div className="input-group px-2 pb-2">
                <input type="text" 
                    className="form-control" 
                    placeholder="Ask a question" 
                    aria-label="Ask a question" 
                    aria-describedby="chatbot-send-btn" 
                    onChange={handleMessageChange}
                    onKeyDown={handleMessageKeyDown}
                    value={messageInput}
                />
                <button className="btn btn-outline-secondary" 
                    type="button" 
                    id="chatbot-send-btn"
                    onClick={() => chatQuery.mutate(messageInput)}
                >Ask</button>
            </div>
        </div>
    );
}
