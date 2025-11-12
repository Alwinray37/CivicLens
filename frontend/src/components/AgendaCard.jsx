import styles from './AgendaCard.module.css';

import { timeStrToSeconds } from '../util/time';

/* 
    * Card to display the agenda items of a meeting
    * props:
        * events: {
            * itemNum: string
                * Item number of the agenda item
            * fileNum: string
                * File number of the agenda item
            * content: string 
                * Agenda description
            * timespan: string
                * Timespan at which this agenda item occurs
            * }[]
        * onItemClick: (seconds) => any;
            * Function that is called when a transcript item is clicked.
            * The function takes in the seconds value of the transcript's
            * time and returns any value
*/
export default function AgendaCard({
    events,
    onItemClick,
}) {
    return (
        <div className={"container p-0 d-flex flex-column bg-body-secondary "
                        + styles.agendaCard}>
            <div className="overflow-y-scroll py-2 d-flex flex-column gap-2 flex-grow-1 min-scrollbar">
                {events.map((e, i) =>
                <div className={"bg-body-tertiary shadow-sm rounded rounded-2 p-3 mx-2 "
                                + styles.agendaItem}
                    onClick={() => onItemClick?.(timeStrToSeconds(e.timespan.split('-')[0]))}
                    key={i}
                >
                    <span className="text-start text-md text-body-secondary fw-bold d-block mb-1">NO. ({e.itemNum}) - {e.fileNum}</span>
                    <span className="text-start d-block text-body-secondary mb-1">{e.content}</span>
                    <span className="text-start d-block text-body-tertiary">{e.timespan}</span>
                </div>
                )}
            </div>
        </div>
    );
}
