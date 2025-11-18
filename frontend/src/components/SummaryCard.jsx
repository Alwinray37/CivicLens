import styles from './SummaryCard.module.css';

import { srtTimeStrToSeconds, timeStrToSeconds } from "../util/time";

export default function SummaryCard({
    summaries,
    onItemClick,
}) {

    const sortedSummaries = [...summaries].sort((a, b) => a.StartTime.localeCompare(b.StartTime))

    return (
        <div className={"container p-0 d-flex flex-column bg-body-secondary "
                        + styles.summaryCard}>
            <div className="overflow-y-scroll py-2 d-flex flex-column gap-2 flex-grow-1 min-scrollbar">
                {
                sortedSummaries && sortedSummaries.length > 0 ?
                sortedSummaries.map((s, i) =>
                <div className={"bg-body-tertiary shadow-sm rounded rounded-2 p-3 mx-2 "
                                + styles.summaryItem}
                    onClick={() => onItemClick?.(srtTimeStrToSeconds(s.StartTime))}
                    key={i}
                >
                    <span className="text-start text-md text-body-secondary fw-bold d-block mb-1">{s.Title}</span>
                    <span className="text-start d-block text-body-secondary mb-1">{s.Summary}</span>
                    <span className="text-start d-block text-body-tertiary">{s.StartTime.split(',').at(0)}</span>
                </div>
                )
                :
                <p className="mt-3">There are no summaries for this video</p>
                }
            </div>
        </div>
    )
}
