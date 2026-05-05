import { TAG_DEFINITIONS } from '@util/tagDefinitions';

const FIELD_WEIGHTS = {
    agendaTitle: 4,
    agendaDescription: 3,
    summaryTitle: 3,
    summaryBody: 2,
};

const MIN_TAG_SCORE = 3;
const MAX_TAGS_PER_MEETING = 3;

export function normalizeText(text) {
    return String(text || '')
        .toLowerCase()
        .replace(/[^a-z0-9\s]/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
}

function countPhraseMatches(text, phrases) {
    if (!text || !phrases?.length) return 0;

    return phrases.reduce((count, phrase) => {
        const normalizedPhrase = normalizeText(phrase);
        return normalizedPhrase && text.includes(normalizedPhrase) ? count + 1 : count;
    }, 0);
}

function countKeywordMatches(text, keywords) {
    if (!text || !keywords?.length) return 0;

    return keywords.reduce((count, keyword) => {
        const normalizedKeyword = normalizeText(keyword);
        if (!normalizedKeyword) return count;

        const pattern = new RegExp(`\\b${normalizedKeyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'g');
        return count + ((text.match(pattern) || []).length > 0 ? 1 : 0);
    }, 0);
}

function scoreField(text, definition, weight) {
    const normalizedText = normalizeText(text);
    if (!normalizedText) return 0;

    const phraseMatches = countPhraseMatches(normalizedText, definition.phrases);
    const keywordMatches = countKeywordMatches(normalizedText, definition.keywords);

    return (phraseMatches * weight) + (keywordMatches * Math.max(1, weight - 1));
}

export function inferTagsFromMeetingDetails(detailData) {
    if (!detailData) return [];

    const agenda = Array.isArray(detailData.agenda) ? detailData.agenda : [];
    const summaries = Array.isArray(detailData.summaries) ? detailData.summaries : [];

    const scoredTags = TAG_DEFINITIONS.map((definition) => {
        let score = 0;

        agenda.forEach((item) => {
            score += scoreField(item?.Title, definition, FIELD_WEIGHTS.agendaTitle);
            score += scoreField(item?.Description, definition, FIELD_WEIGHTS.agendaDescription);
        });

        summaries.forEach((summary) => {
            score += scoreField(summary?.Title, definition, FIELD_WEIGHTS.summaryTitle);
            score += scoreField(summary?.Summary, definition, FIELD_WEIGHTS.summaryBody);
        });

        return {
            id: definition.id,
            label: definition.label,
            score,
        };
    });

    return scoredTags
        .filter((tag) => tag.score >= MIN_TAG_SCORE)
        .sort((a, b) => b.score - a.score || a.label.localeCompare(b.label))
        .slice(0, MAX_TAGS_PER_MEETING)
        .map(({ id, label }) => ({ id, label }));
}
