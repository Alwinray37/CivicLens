import { timeStrToSeconds } from '@util/time';
import InfoPill from '@components/InfoPill';

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
        <div className="container p-0 d-flex flex-column bg-body-secondary agenda-card">
            <div className="overflow-y-scroll py-2 d-flex flex-column gap-2 flex-grow-1 min-scrollbar">
                {events.map((e, i) =>
                <InfoPill
                    title={`NO. (${e.itemNum}) - ${e.fileNum}`}
                    content={e.content}
                    time={e.timespan}
                    onTimeClick={() => onItemClick?.(timeStrToSeconds(e.timespan?.split('-')[0]))}

                    key={i}
                />
                )}
            </div>
        </div>
    );
}
