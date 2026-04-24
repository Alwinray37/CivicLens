const teamMembers = [
    'Alwin Ray Roble',
    'Alexander Leontiev',
    'Thomas Scott',
    'Nikita Ulianov',
];

const projectHighlights = [
    'Meeting videos paired with AI-generated summaries and agenda breakdowns',
    'Search and topic filters for locating relevant Los Angeles meetings faster',
    'A meeting-specific chatbot and timeline tools for jumping to important moments',
];

const stackItems = [
    'Frontend built with React and Vite',
    'Backend API powered by Python and FastAPI',
    'Docker Compose used to coordinate project services and infrastructure',
    'Model and processing pipelines used to generate transcripts, summaries, and related meeting artifacts',
];

const nextSteps = [
    'Expand meeting coverage and improve consistency across council and committee sessions',
    'Refine summary, transcript, and chatbot quality as models and data pipelines improve',
    'Continue improving navigation, search, and issue discovery for residents and researchers',
];

export default function AboutPage() {
    return (
        <div className="container about-page">
            <section className="about-hero app-panel text-start">
                <p className="about-eyebrow mb-2">About CivicLens</p>
                <h1 className="about-title">A senior design project focused on civic accessibility.</h1>
                <p className="about-lead mb-0">
                    CivicLens is a California State University, Northridge Computer Science senior project
                    designed to help people follow Los Angeles City Council and committee meetings more
                    efficiently. The site brings together public meeting recordings with AI-assisted summaries,
                    agenda context, transcripts, and interactive tools so users can review government
                    discussions without having to watch every meeting from start to finish.
                </p>
            </section>

            <section className="about-grid">
                <article className="about-card app-panel text-start">
                    <h2 className="about-card-title">Purpose</h2>
                    <p className="about-body mb-0">
                        The goal of the project is both practical and academic. CivicLens explores how
                        software and AI can make local government information easier to access, while also
                        serving as a substantial senior design effort in full-stack application development.
                        It is intended as a prototype with real public-use potential, especially for
                        residents, journalists, students, and community advocates who need faster ways to
                        understand what happened in a meeting.
                    </p>
                </article>

                <article className="about-card app-panel text-start">
                    <h2 className="about-card-title">How It Works</h2>
                    <ul className="about-list mb-0">
                        {projectHighlights.map((item) => (
                            <li key={item}>{item}</li>
                        ))}
                    </ul>
                </article>

                <article className="about-card app-panel text-start">
                    <h2 className="about-card-title">Project Stack</h2>
                    <ul className="about-list mb-0">
                        {stackItems.map((item) => (
                            <li key={item}>{item}</li>
                        ))}
                    </ul>
                </article>

                <article className="about-card app-panel text-start">
                    <h2 className="about-card-title">Senior Project Team</h2>
                    <p className="about-body">
                        CivicLens was developed as a CSUN Computer Science senior design group project.
                    </p>
                    <ul className="about-list mb-0">
                        {teamMembers.map((member) => (
                            <li key={member}>{member}</li>
                        ))}
                    </ul>
                </article>

                <article className="about-card app-panel text-start about-card-wide">
                    <h2 className="about-card-title">Limitations And Future Work</h2>
                    <p className="about-body">
                        Because this project depends on generated artifacts such as transcripts, summaries,
                        and chatbot responses, some information may be incomplete or imperfect. Meeting
                        coverage can also vary depending on available data and processing status. These are
                        important limitations for an academic prototype, and they also define the next stage
                        of improvement.
                    </p>
                    <ul className="about-list mb-0">
                        {nextSteps.map((item) => (
                            <li key={item}>{item}</li>
                        ))}
                    </ul>
                </article>
            </section>
        </div>
    );
}
