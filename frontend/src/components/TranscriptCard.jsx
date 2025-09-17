import styles from './TranscriptCard.module.css';

export default function TranscriptCard({
    snippets,
}) {
    return (
        <div className={"container border p-2 d-flex flex-column "
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
