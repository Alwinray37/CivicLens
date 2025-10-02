import styles from './ChatbotMessage.module.css';

/*
    * Message bubble for the chatbot
    * props:
        * message: string
            * content of the chat
        * type: "outgoing" | "incoming"
                * outgoing messages appear on right, outgoing appear on left
*/
export default function ChatbotMessage({
    message,
    type="outgoing",
}) {
    return (
        <div className={`d-flex 
                    ${type === "outgoing" 
                        ? "justify-content-end" 
                        : "justify-content-start"} 
                    w-100`}>
            <span className={"border rounded-1 py-1 px-2 my-1 d-inline-block "
                            + styles.chatbotMessage}>
                {message}
            </span>
        </div>
    )
}
