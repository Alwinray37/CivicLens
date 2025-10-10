import styles from './BookmarkCard.module.css';

/* 
    * Card to display a video's bookmarks
    * props:
        * bookmarks: {
                * title: string
                    * title of the bookmark
                * description: string
                    * description of the bookmark
                * time: string
                    * formatted string of the time at which this bookmark is set to
            * }[]
*/
export default function BookmarkCard({
    bookmarks
}) {
    return (
        <div className={"container rounded p-0 d-flex flex-column bg-body-secondary "
                        + styles.bookmarkCard}>
            <h4 className="mx-2 py-2 ps-1 mb-0 border-bottom text-start text-body-secondary fw-bold">Bookmarks</h4>
            <div className="overflow-scroll py-2 d-flex flex-column gap-1 flex-grow-1">
                {bookmarks.map((b, i) =>
                <div className="bg-body-tertiary shadow-sm rounded rounded-2 p-3 mx-2 d-flex justify-content-between"
                    key={i}
                >
                    <div>
                        <span className="text-start d-block mb-1 text-body-secondary">{b.title}</span>
                        <span className={"d-block text-start text-body-tertiary "
                                        + styles.bookmarkDescription}>{b.description}</span>
                    </div>
                    <span className="d-block text-end text-body-tertiary">{b.time}</span>
                </div>
                )}
            </div>
        </div>
    )
}
