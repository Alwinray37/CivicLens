import 'bootstrap';
import AgendaCard from '@components/AgendaCard';
import SummaryCard from '@components/SummaryCard';

// bootstrap button class list for tabs
let bs_btn_clslst = `
    nav-link
    w-100
    `;

export default function VideoInfoCard({
    videoData,
    onTimeSelect
}) {
    return (
        // VideoInfo Component 
        <div className="app-panel video-info-shell rounded p-0 shadow-sm">
            {/* Navbar for video info tabs */}
            <ul id="info-tab-container" className="nav nav-pills p-2 isolate rounded-top d-flex justify-content-center gap-2 video-info-tabs" role="tablist">
                <li className="video-info-nav-item" role="presentation">
                    <button className={`${bs_btn_clslst} active video-info-nav-link`} id="video-summary-tab" data-bs-toggle="pill" data-bs-target="#video-summary" type="button" role="tab" aria-controls="video-summary" aria-selected="true">
                        <span className="video-info-tab-eyebrow">Overview</span>
                        <span className="video-info-tab-label">Summary</span>
                    </button>
                </li>
                <li className="video-info-nav-item" role="presentation">
                    <button className={`${bs_btn_clslst} video-info-nav-link`} id="video-agenda-tab" data-bs-toggle="pill" data-bs-target="#video-agenda" type="button" role="tab" aria-controls="video-agenda" aria-selected="false">
                        <span className="video-info-tab-eyebrow">Meeting Flow</span>
                        <span className="video-info-tab-label">Agenda</span>
                    </button>
                </li>
            </ul>
            <div className="tab-content overflow-hidden rounded-bottom" id="video-tabContent">
                <div className="tab-pane fade show active" id="video-summary" role="tabpanel" aria-labelledby="video-summary-tab" tabIndex={0}>
                    <SummaryCard 
                        onItemClick={onTimeSelect}
                        summaries={videoData.summaries}
                    />
                </div>
                <div className="tab-pane fade" id="video-agenda" role="tabpanel" aria-labelledby="video-agenda-tab" tabIndex={0}>
                     <AgendaCard 
                         events={
                             videoData.agenda.map(a => ({
                                 itemNum: a.ItemNumber,
                                 fileNum: a.FileNumber,
                                 content: a.Title,
                             }))
                         }
                     onItemClick={onTimeSelect}
                     />
                </div>
            </div>
        </div>
    );
}
