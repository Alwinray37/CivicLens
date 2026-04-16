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
}) {
    return (
        <div className={`d-flex 
                    ${type === "outgoing" 
                        ? "justify-content-end pe-2" 
                        : "justify-content-start ps-2"} 
                    w-100`}>
            <span 
            className={`shadow-sm rounded-1 py-1 px-2 my-1 d-inline-block text-body-secondary ${styles.chatbotMessage}`}
            data-type={type}
            >
                {
                    type === "pending" 
                    ? message.split('').map((c, i) => 
                        <span key={i} className={styles.loadingChar}>{c}</span>
                    )
                    : message
                }
            </span>
        </div>
    )
}
