import Timestamp from "./Timestamp"

export default function InfoPill({
    title,
    content,
    time,
    onTimeSelect,
    ...rest
}) {
    return (
        <div className="app-surface-muted shadow-sm rounded rounded-2 p-3 mx-2 text-start info-item"
        {...rest}
        >
            <span className="text-md info-item-title fw-bold d-block mb-1">{title}</span>
            <span className="d-block info-item-content mb-1">{content}</span>
            {time &&
                <Timestamp
                    time={time}
                    onTimeSelect={onTimeSelect}
                    withEmphasis={true}
                />
            }
        </div>
    )
}
