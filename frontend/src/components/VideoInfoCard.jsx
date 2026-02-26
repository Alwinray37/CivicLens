import styles from './VideoInfoCard.module.css';

import 'bootstrap';
import TranscriptCard from '@components/TranscriptCard';
import AgendaCard from '@components/AgendaCard';
import SummaryCard from '@components/SummaryCard';
import TimelineCard from '@components/TimelineCard';

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
        <div className="bg-body-secondary rounded p-0 shadow-sm ">
            <ul className={`nav nav-pills p-2 shadow-sm isolate rounded-top d-flex justify-content-center ${styles.tabs}`} id="video-info-tab" role="tablist">
                <li className={styles.navItem} role="presentation">
                    <button className={`${bs_btn_clslst} active ${styles.navLink}`} id="video-summary-tab" data-bs-toggle="pill" data-bs-target="#video-summary" type="button" role="tab" aria-controls="video-summary" aria-selected="true">Summary</button>
                </li>
                <li className={styles.navItem} role="presentation">
                    <button className={`${bs_btn_clslst} ${styles.navLink}`} id="video-agenda-tab" data-bs-toggle="pill" data-bs-target="#video-agenda" type="button" role="tab" aria-controls="video-agenda" aria-selected="false">Agenda</button>
                </li>
                <li className={styles.navItem} role="presentation">
                    <button className={bs_btn_clslst} id="video-transcript-tab" data-bs-toggle="pill" data-bs-target="#video-transcript" type="button" role="tab" aria-controls="video-transcript" aria-selected="false" >Transcript</button>
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
                <div className="tab-pane fade" id="video-transcript" role="tabpanel" aria-labelledby="video-transcript-tab" tabIndex={0}>
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
