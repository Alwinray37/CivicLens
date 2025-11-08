import 'bootstrap';
import TranscriptCard from './TranscriptCard';
import AgendaCard from './AgendaCard';
import SummaryCard from './SummaryCard';
import TimelineCard from './TimelineCard';

export default function VideoInfoCard({
    videoData,
    onTimeSelect
}) {
    return (
        <div className="bg-body-secondary rounded p-0 shadow-sm ">
            <ul className="nav nav-pills bg-body-tertiary p-2 rounded-top d-flex justify-content-center gap-3 " id="video-info-tab" role="tablist">
                <li className="nav-item" role="presentation">
                    <button className="nav-link active" id="video-summary-tab" data-bs-toggle="pill" data-bs-target="#video-summary" type="button" role="tab" aria-controls="video-summary" aria-selected="true">Summary</button>
                </li>
                <li className="nav-item" role="presentation">
                    <button className="nav-link" id="video-agenda-tab" data-bs-toggle="pill" data-bs-target="#video-agenda" type="button" role="tab" aria-controls="video-agenda" aria-selected="false">Agenda</button>
                </li>
                <li className="nav-item" role="presentation">
                    <button className="nav-link" id="video-timeline-tab" data-bs-toggle="pill" data-bs-target="#video-timeline" type="button" role="tab" aria-controls="video-timeline" aria-selected="false">Timeline</button>
                </li>
                <li className="nav-item" role="presentation">
                    <button className="nav-link" id="video-transcript-tab" data-bs-toggle="pill" data-bs-target="#video-transcript" type="button" role="tab" aria-controls="video-transcript" aria-selected="false" >Transcript</button>
                </li>
            </ul>
            <div className="tab-content overflow-hidden rounded-bottom" id="video-tabContent">
                <div className="tab-pane fade show active" id="video-summary" role="tabpanel" aria-labelledby="video-summary-tab" tabIndex="0">
                    <SummaryCard />
                </div>
                <div className="tab-pane fade" id="video-agenda" role="tabpanel" aria-labelledby="video-agenda-tab" tabIndex="0">
                     <AgendaCard 
                         events={
                             videoData.agenda.map(a => ({
                                 itemNum: a.ItemNumber,
                                 fileNum: a.FileNumber,
                                 content: a.Title,
                                 timespan: "5:00",
                             }))
                         }
                     onItemClick={onTimeSelect}
                     />
                </div>
                <div className="tab-pane fade" id="video-timeline" role="tabpanel" aria-labelledby="video-timeline-tab" tabIndex="0">
                    <TimelineCard />
                </div>
                <div className="tab-pane fade" id="video-transcript" role="tabpanel" aria-labelledby="video-transcript-tab" tabIndex="0">
                     <TranscriptCard 
                         onItemClick={onTimeSelect}
                         snippets={[
                         {
                             time: "2:57",
                             content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                         },
                         {
                             time: "5:57",
                             content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                         },
                         {
                             time: "10:57",
                             content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                         },
                         {
                             time: "20:00",
                             content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
                         },
                     ]}/>
                </div>
            </div>
        </div>
    );
}
