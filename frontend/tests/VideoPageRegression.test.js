import { assert, describe, expect, test } from "vitest";
import { fetchVideoData } from "../src/util/videoPageUtility";
import { srtTimeStrToSeconds } from "../src/util/time";


describe('video page retrieves correct data format and translates timestamps', async () => {

    test('connection to api', () => {
        assert.doesNotThrow(() => fetchVideoData(4), 'An error occurred fetching meeting data');
    })

    const data = await fetchVideoData(4);
    const { meeting, agenda, summaries } = data;

    test('video page correct data format', () => {

        // assert top level objects
        expect(Array.isArray(agenda)).toBe(true);
        expect(Array.isArray(summaries)).toBe(true);
        expect(typeof meeting).toBe('object');


        // assert meeting data
        expect(typeof meeting.Date).toBe('string');
        expect(typeof meeting.Title).toBe('string');
        expect(typeof meeting.VideoURL).toBe('string');
        expect(typeof meeting.MeetingID).toBe('number');


        function assertAgendaData(agenda) {
            expect(typeof agenda.Title).toBe('string');
            expect(typeof agenda.MeetingID).toBe('number');
            expect(typeof agenda.FileNumber).toBe('string');
            expect(typeof agenda.ItemNumber).toBe('number');
            expect(typeof agenda.Description).toBe('string');
            expect(typeof agenda.OrderNumber).toBe('number');
            expect(typeof agenda.AgendaItemID).toBe('number');
        }
        agenda.forEach((a) => assertAgendaData(a));


        function assertSummaryData(summary) {
            expect(typeof summary.Title).toBe('string');
            expect(typeof summary.Summary).toBe('string');
            expect(typeof summary.MeetingID).toBe('number');
            expect(typeof summary.StartTime).toBe('string');
            expect(typeof summary.SummaryId).toBe('number');
        }
        summaries.forEach((s) => assertSummaryData(s));


    })

    test("summary timestamp conversion doesn't fail", () => {
        summaries.forEach(s => {
            // -1 is returned when there is a problem with srt format
            expect(srtTimeStrToSeconds(s.StartTime)).not.toEqual(-1);
        })
    })

    test('srt timestamp translation works as expected', () => {
        const srtTimestamp = '02:20:50,878';
        const expected = 8450;
        const actual = srtTimeStrToSeconds(srtTimestamp);

        expect(actual).toBe(expected);
    });
})
