/* takes a time string like "2:35" and
    * converts it to a number in seconds (155)
    *
    * a returned time of -1 means the function 
    * failed to convert the time string to a number
*/
export const timeStrToSeconds = (timeStr) => {
    if(typeof timeStr !== 'string') return -1;

    const split = timeStr.split(":");
    if(split.length !== 2) return -1;

    const convMin = Number.parseInt(split[0]);
    if(Number.isNaN(convMin)) return -1;

    const convSec = Number.parseInt(split[1]);
    if(Number.isNaN(convSec)) return -1;

    return convMin * 60 + convSec;
}


/* takes a time string like "01:42:16,715" (SRT FORMAT) and
    * converts it to a number in seconds (155)
    *
    * a returned time of -1 means the function 
    * failed to convert the time string to a number
*/
export const srtTimeStrToSeconds = (timeStr) => {
    if(typeof timeStr !== 'string') return -1;

    const split = timeStr.split(":");
    if(split.length !== 3) return -1;

    const convHours = Number.parseInt(split[0]);
    if(Number.isNaN(convHours)) return -1;

    const convMin = Number.parseInt(split[1]);
    if(Number.isNaN(convMin)) return -1;

    // ignore milliseconds from srt time
    const secStr = split[2].split(',')[0];
    const convSec = Number.parseInt(secStr);
    if(Number.isNaN(convSec)) return -1;

    return convHours * 3600 + convMin * 60 + convSec;
}
