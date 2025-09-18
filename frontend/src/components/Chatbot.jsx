import { useState } from 'react';
import styles from './Chatbot.module.css';

import ChatbotMessage from './ChatbotMessage';

export default function Chatbot() {
    const [messages, setMessages] = useState([
        {
            type: "outgoing",
            message: "What was the main purpose of this meeting?",
        },
        {
            type: "incoming",
            message: "The purpose of this meeting was to...",
        },
        {
            type: "outgoing",
            message: "What was the main purpose of this meeting?",
        },
        {
            type: "incoming",
            message: "The purpose of this meeting was to...",
        },
        {
            type: "outgoing",
            message: "What was the main purpose of this meeting?",
        },
        {
            type: "incoming",
            message: "The purpose of this meeting was to...",
        },
        {
            type: "outgoing",
            message: "What was the main purpose of this meeting?",
        },
        {
            type: "incoming",
            message: "The purpose of this meeting was to...",
        },
    ]);

    return (
        <div className={"container border text-start p-2 h-100 d-flex flex-column justify-content-between bg-light "
                        + styles.chatbotWrapper}>
            <h4 className="border-bottom m-0 ps-1 pb-2">Chatbot</h4>
            <div className="d-flex flex-column flex-grow-1 overflow-scroll">
                {messages.map((m, i) =>
                    <ChatbotMessage message={m.message} type={m.type} key={i}/>
                )}
            </div>
            <div className="input-group">
                <input type="text" 
                    className="form-control" 
                    placeholder="Ask a question" 
                    aria-label="Ask a question" 
                    aria-describedby="chatbot-send-btn" />
                <button className="btn btn-outline-secondary" 
                    type="button" 
                    id="chatbot-send-btn">Ask</button>
            </div>
        </div>
    );
}
