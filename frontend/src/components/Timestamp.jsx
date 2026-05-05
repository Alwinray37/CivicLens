export default function Timestamp({
    time,
    onTimeSelect,
    withEmphasis=false,
    }) {
    return (
        <span 
            className="d-inline-block info-pill-time"
            onClick={() => onTimeSelect(time)}
        >
            <span>{time}</span>
            {withEmphasis &&
            <span className="ms-2 text-sm text-info-emphasis info-pill-time-info">Jump to time</span>
            }
        </span>
    )
}
