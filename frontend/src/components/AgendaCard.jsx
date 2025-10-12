import styles from './AgendaCard.module.css';

/* 
    * Card to display the agenda items of a meeting
    * props:
        * events: {
            * content: string 
                * Agenda description
            * timespan: string
                * Timespan at which this agenda item occurs
            * }[]
*/
export default function AgendaCard({
    events,
}) {
    return (
        <div className={"container rounded p-0 d-flex flex-column bg-body-secondary "
                        + styles.agendaCard}>
            <h4 className="mb-0 mx-2 py-2 ps-1 border-bottom text-start text-body-secondary fw-bold">Agenda</h4>
            <div className="overflow-scroll py-2 d-flex flex-column gap-2 flex-grow-1">
                {events.map((e, i) =>
                <div className="bg-body-tertiary shadow-sm rounded rounded-2 p-3 mx-2"
                    key={i}
                >
                    <span className="text-start d-block mb-1 text-body-secondary ">{e.content}</span>
                    <span className="d-block text-start text-body-tertiary ">{e.timespan}</span>
                </div>
                )}
            </div>
        </div>
    );
}
