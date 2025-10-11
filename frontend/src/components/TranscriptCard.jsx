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
    onItemClick,
}) {
    /* takes a time string like "2:35" and
        * converts it to a number in seconds (155)
        *
        * a returned time of -1 means the function 
        * failed to convert the time string to a number
    */
    const timeStrToSeconds = (timeStr) => {
        const split = timeStr.split(":");
        if(split.length !== 2) return -1;

        const convMin = Number.parseInt(split[0]);
        if(Number.isNaN(convMin)) return -1;

        const convSec = Number.parseInt(split[1]);
        if(Number.isNaN(convSec)) return -1;

        return convMin * 60 + convSec;
    }

    return (
        <div className={"container p-0 rounded d-flex flex-column bg-body-secondary "
                        + styles.transcriptCard}>
            <h4 className="py-2 mx-2 mb-0 border-bottom ps-1 text-start text-body-secondary fw-bold">Transcript</h4>
            <div className="py-2 overflow-scroll d-flex flex-column gap-2 flex-grow-1 ">
                {snippets.map((s, i) => 
                    <div className={"bg-body-tertiary shadow-sm rounded rounded-2 mx-2 p-3 d-flex justify-content-between "
                                    + styles.transcriptItem}
                        key={i}
                        onClick={() => onItemClick?.(timeStrToSeconds(s.time))}
                    >
                        <span className={"text-start text-body-tertiary text-truncate me-1" + styles.transcriptTime}>{s.time}</span>
                        <span className={"text-start text-body-secondary " + styles.transcriptText}>{s.content}</span>
                    </div>
                )}
            </div>
        </div>
    )
}
