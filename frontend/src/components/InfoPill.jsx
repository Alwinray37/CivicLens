export default function InfoPill({
    title,
    content,
    time,
    onTimeClick,
    ...rest
}) {
    return (
        <div className="bg-body-tertiary shadow-sm rounded rounded-2 p-3 mx-2 text-start info-item"
        {...rest}
        >
            <span className="text-md text-body-secondary fw-bold d-block mb-1">{title}</span>
            <span className="d-block text-body-secondary mb-1">{content}</span>
            {time &&
            <span 
                className="d-inline-block text-body-tertiary info-pill-time"
                onClick={() => onTimeClick(time)}
            >
                <span>{time.split(',').at(0)}</span>
                <span className="ms-2 text-sm text-info-emphasis info-pill-time-info">Jump to time</span>
            </span>
            }
        </div>
    )
}
