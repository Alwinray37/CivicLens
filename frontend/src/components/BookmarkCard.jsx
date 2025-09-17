import styles from './BookmarkCard.module.css';

export default function BookmarkCard({
    bookmarks
}) {
    return (
        <div className={"container border p-2 d-flex flex-column "
                        + styles.bookmarkCard}>
            <h4 className="m-0 pb-2 ps-2 border-bottom text-start">Bookmarks</h4>
            <div className="overflow-scroll pt-2 d-flex flex-column gap-1 flex-grow-1">
                {bookmarks.map((b, i) =>
                <div className="border rounded rounded-2 p-3 d-flex justify-content-between"
                    key={i}
                >
                    <div>
                        <span className="text-start d-block mb-1">{b.title}</span>
                        <span className={"d-block text-start "
                                        + styles.bookmarkDescription}>{b.description}</span>
                    </div>
                    <span className="d-block text-end">{b.time}</span>
                </div>
                )}
            </div>
        </div>
    )
}
