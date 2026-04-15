import { describe, expect, test } from 'vitest';

import { getTimezoneDate, srtTimeStrToSeconds, timeStrToSeconds } from '../../src/util/time';

describe('timeStrToSeconds', () => {
    test('converts mm:ss to seconds', () => {
        expect(timeStrToSeconds('2:35')).toBe(155);
    });

    test('returns -1 for invalid string input', () => {
        expect(timeStrToSeconds('bad')).toBe(-1);
    });

    test('returns -1 for non-string input', () => {
        expect(timeStrToSeconds(155)).toBe(-1);
    });
});

describe('srtTimeStrToSeconds', () => {
    test('converts SRT timestamps to seconds', () => {
        expect(srtTimeStrToSeconds('02:20:50,878')).toBe(8450);
    });

    test('returns -1 for invalid SRT strings', () => {
        expect(srtTimeStrToSeconds('02:20')).toBe(-1);
    });

    test('returns -1 for non-string input', () => {
        expect(srtTimeStrToSeconds(null)).toBe(-1);
    });
});

describe('getTimezoneDate', () => {
    test('returns a Date instance', () => {
        const date = getTimezoneDate(new Date('2025-01-01T00:00:00Z'));

        expect(date).toBeInstanceOf(Date);
        expect(Number.isNaN(date.getTime())).toBe(false);
    });

    test('uses the current date when no argument is provided', () => {
        const date = getTimezoneDate();

        expect(date).toBeInstanceOf(Date);
    });
});
