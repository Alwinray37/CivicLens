import styles from './TranscriptCard.module.css';

/*
    * Card to display transcript words next to the time at which they were spoken
    * props:
        * snippets: {
            * time: string
                * formatted string of the time at which the words were said
            * content: string
                * the words that were said at a certain time
        * }[]
*/
export default function TranscriptCard({
    snippets,
}) {
    return (
        <div className={"container border p-2 d-flex flex-column bg-light "
                        + styles.transcriptCard}>
            <h4 className="m-0 pb-2 border-bottom ps-1 text-start">Transcript</h4>
            <div className="overflow-scroll pt-2 d-flex flex-column gap-1 flex-grow-1">
                {snippets.map((s, i) => 
                    <div className="border rounded rounded-2 p-3 d-flex justify-content-between"
                        key={i}
                    >
                        <span className={"text-start " + styles.transcriptTime}>{s.time}</span>
                        <span className={"text-start " + styles.transcriptText}>{s.content}</span>
                    </div>
                )}
            </div>
        </div>
    )
}
