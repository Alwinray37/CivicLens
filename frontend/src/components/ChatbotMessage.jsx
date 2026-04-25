import { secondsToHHMMSS } from "@/util/time";
import { useEffect, useState } from "react";
import Timestamp from "./Timestamp";

/*
    * Message bubble for the chatbot
    * props:
    * message: string
    * content of the chat
    * type: "outgoing" | "incoming" | "error" | "pending"
    * outgoing messages appear on right, outgoing appear on left
    */
    export default function ChatbotMessage({
        message,
        type="outgoing",
        onTimeSelect,
    }) {
        const variantClass = {
            outgoing: 'chatbot-message-outgoing',
            incoming: 'chatbot-message-incoming',
            error: 'chatbot-message-error',
            pending: 'chatbot-message-pending',
        }[type] || 'chatbot-message-incoming';

        const [parsedMessage, setParsedMessage] = useState(message);

        function parseChatbotMessage(message) {
            let elements = [];

            // chatbot *should* return [TIME: n] where n is some number
            // sometimes it leaves artifacts and response as [Start Time: n seconds]
            // or [Time: n seconds], so wildcards are in place to catch that
            let regex = /\[.*TIME: (\d+\.?\d*).*\]/i;
            let start = 0;
            while(true) {
                let execResult = regex.exec(message.slice(start));

                // if no timestamp match
                if(execResult == null) break;

                // push previous text
                elements.push(message.slice(start, start + execResult.index));

                let time = Number.parseInt(execResult[1])

                start += execResult.index + execResult[0].length;

                // push timestamp
                elements.push(<Timestamp key={start} time={secondsToHHMMSS(time)} onTimeSelect={() => onTimeSelect(time)} />);
            }
            if(start < message.length) {
                elements.push(message.slice(start));
            }

            return <>{[...elements]}</>
        }

        useEffect(() => {
            setParsedMessage(parseChatbotMessage(message))
        }, [message]);

        return (
            <div className={`d-flex 
                ${type === "outgoing" 
                        ? "justify-content-end pe-2" 
                        : "justify-content-start ps-2"} 
                w-100`}>
            <span 
            className={`shadow-sm rounded-1 py-1 px-2 my-1 d-inline-block chatbot-message ${variantClass}`}
            data-type={type}
            >
            {
                type === "pending" 
                ? message.split('').map((c, i) => 
                    <span key={i} className="chatbot-loading-char">{c}</span>
                )
                : parsedMessage
            }
            </span>
            </div>
        )
    }

