import styles from './InfoPill.module.css';

export default function InfoPill({
    title,
    content,
    time,
    onTimeClick,
    ...rest
}) {
    return (
        <div className={`bg-body-tertiary shadow-sm rounded rounded-2 p-3 mx-2 text-start ${styles.infoItem}`}
        {...rest}
        >
            <span className="text-md text-body-secondary fw-bold d-block mb-1">{title}</span>
            <span className="d-block text-body-secondary mb-1">{content}</span>
            <span 
                className={`d-inline-block text-body-tertiary ${styles.time}`}
                onClick={() => onTimeClick(time)}
            >
                <span>{time.split(',').at(0)}</span>
                <span className={`ms-2 text-sm text-info-emphasis ${styles.timeInfo}`}>Jump to time</span> </span>
        </div>
    )
}
