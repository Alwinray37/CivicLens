export default function AgendaCard({
    events,
}) {
    return (
        <div className="container border p-2">
            <h4 className="m-0 pb-2 ps-2 border-bottom text-start">Agenda</h4>
            <div className="overflow-scroll pt-2 d-flex flex-column gap-1">
                {events.map((e, i) =>
                <div className="border rounded rounded-2 p-3"
                    key={i}
                >
                    <span className="text-start d-block mb-1">{e.content}</span>
                    <span className="d-block text-start">{e.timespan}</span>
                </div>
                )}
            </div>
        </div>
    );
}
