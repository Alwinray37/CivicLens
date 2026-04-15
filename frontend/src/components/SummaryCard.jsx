import InfoPill from '@components/InfoPill';

import { srtTimeStrToSeconds } from "@util/time";

export default function SummaryCard({
    summaries,
    onItemClick,
}) {

    const sortedSummaries = summaries ? [...summaries].sort((a, b) => a.StartTime.localeCompare(b.StartTime)) : [];

    return (
        <div className="container p-0 d-flex flex-column app-panel summary-card">
            <div className="overflow-y-scroll py-2 d-flex flex-column gap-2 flex-grow-1 min-scrollbar">
                {
                sortedSummaries && sortedSummaries.length > 0 ?
                sortedSummaries.map((s, i) =>
                    
                <InfoPill
                    title={s.Title}
                    content={s.Summary}
                    time={s.StartTime}
                    onTimeClick={() => onItemClick?.(srtTimeStrToSeconds(s.StartTime))}

                    key={i}
                />
                )
                :
                <p className="mt-3 empty-state-text">There are no summaries for this video</p>
                }
            </div>
        </div>
    )
}
