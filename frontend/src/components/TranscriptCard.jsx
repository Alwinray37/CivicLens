import styles from './TranscriptCard.module.css';
import { timeStrToSeconds } from '../util/time';

/*
    * Card to display transcript words next to the time at which they were spoken
    * props:
        * snippets: {
            * time: string
                * formatted string of the time at which the words were said
            * content: string
                * the words that were said at a certain time
        * onItemClick: (seconds) => any;
            * Function that is called when a transcript item is clicked.
            * The function takes in the seconds value of the transcript's
            * time and returns any value
        * }[]
*/
export default function TranscriptCard({
    snippets,
    onItemClick,
}) {

    return (
        <div className={"container p-0 d-flex flex-column bg-body-secondary "
                        + styles.transcriptCard}>
            <div className="py-2 overflow-y-scroll min-scrollbar d-flex flex-column gap-2 flex-grow-1 ">
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
