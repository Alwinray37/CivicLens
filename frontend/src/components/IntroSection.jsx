export default function IntroSection({ onBrowseMeetings }) {
    return (
        <section className="catalog-intro app-panel">
            <div className="catalog-intro-copy text-start">
                <p className="catalog-intro-eyebrow mb-2">Welcome to CivicLens</p>
                <h1 className="catalog-intro-title">Follow Los Angeles council meetings faster.</h1>
                <p className="catalog-intro-text mb-0">
                    CivicLens helps residents, journalists, and community advocates explore Los Angeles City
                    Council and committee meeting recordings with searchable titles, topic tags, summaries,
                    and tools that make it easier to find the moments that matter.
                </p>
            </div>

            <div className="catalog-intro-steps">
                <article className="catalog-intro-step app-surface-muted text-start">
                    <span className="catalog-intro-step-number">1</span>
                    <h2 className="catalog-intro-step-title">Find a meeting</h2>
                    <p className="catalog-intro-step-text mb-0">
                        Browse recent Los Angeles council and committee meetings or search for a specific session.
                    </p>
                </article>

                <article className="catalog-intro-step app-surface-muted text-start">
                    <span className="catalog-intro-step-number">2</span>
                    <h2 className="catalog-intro-step-title">Narrow by issue</h2>
                    <p className="catalog-intro-step-text mb-0">
                        Use the topic tags to focus on issues like housing, public safety, transportation, or budgeting.
                    </p>
                </article>

                <article className="catalog-intro-step app-surface-muted text-start">
                    <span className="catalog-intro-step-number">3</span>
                    <h2 className="catalog-intro-step-title">Review key moments</h2>
                    <p className="catalog-intro-step-text mb-0">
                        Open a meeting to watch the video, review summaries, and use the timeline and chatbot to jump to agenda items and discussion points.
                    </p>
                </article>
            </div>

            <div className="catalog-intro-actions d-flex flex-wrap gap-2">
                <button type="button" className="catalog-intro-cta" onClick={onBrowseMeetings}>
                    Browse Meetings
                </button>
            </div>
        </section>
    );
}
