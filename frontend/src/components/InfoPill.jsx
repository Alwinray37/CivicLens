import styles from './InfoPill.module.css';

export default function InfoPill({
    title,
    content,
    time,
    ...rest
}) {
    return (
        <div className={"bg-body-tertiary shadow-sm rounded rounded-2 p-3 mx-2 "
            + styles.infoItem}
        {...rest}
        >
            <span className="text-start text-md text-body-secondary fw-bold d-block mb-1">{title}</span>
            <span className="text-start d-block text-body-secondary mb-1">{content}</span>
            <span className="text-start d-block text-body-tertiary">{time.split(',').at(0)}</span>
        </div>
    )
}
