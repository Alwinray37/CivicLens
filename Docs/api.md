# API Documentation

## Overview

This document describes the REST API endpoints available in the Meetings FastAPI service (v0.1.0). The API connects to a PostgreSQL database and provides access to meeting data, including listing all meetings and retrieving detailed information for a specific meeting.

Base URL: `http://<host>/`
Spec: [/openapi.json](/openapi.json)

---

## Endpoint: `GET /getMeetingInfo/{meeting_id}`

### Description

Retrieves detailed information for a specific meeting by its unique integer ID. Internally, this calls the PostgreSQL function `get_meeting_json(%s)` and returns the result as a `MeetingInfo` object.

### Signature

```
GET /getMeetingInfo/{meeting_id}
```

### Parameters

| Name         | Type    | Location | Required | Description                                            |
|--------------|---------|----------|----------|--------------------------------------------------------|
| `meeting_id` | `int`   | path     |  Yes   | The unique numeric identifier of the meeting to retrieve. |

### Return Values

**Response Model:** `MeetingInfo` (returned by alias)

| Status Code | Description                                                  |
|-------------|--------------------------------------------------------------|
| `200`       | Success. Returns a `MeetingInfo` object for the given meeting. |
| `404`       | No meeting found for the provided `meeting_id`.              |
| `422`       | Validation error — `meeting_id` could not be parsed as an integer. |
| `400`       | SQL error when executing the database query.                 |
| `503`       | Database connection failed.                                  |
| `500`       | Unexpected database error.                                   |

### Errors & Exceptions

| Exception / Condition              | HTTP Status | Detail Message                              |
|------------------------------------|-------------|---------------------------------------------|
| `psycopg.OperationalError`         | `503`       | `"Database connection failed: <e>"`         |
| `psycopg.ProgrammingError`         | `400`       | `"SQL error: <e>"`                          |
| `psycopg.Error`                    | `500`       | `"Database error: <e>"`                     |
| Result is `None`                   | `404`       | `"No meetings found"`                       |
| `meeting_id` not a valid integer   | `422`       | FastAPI validation error (auto-generated)   |

### Example

**Request:**
```bash
curl -X GET "http://<host>/getMeetingInfo/42" \
  -H "Accept: application/json"
```

**Response (200 OK):**
```json
{
  "meeting": {
    "id": 42,
    "title": "Weekly Standup",
    "date": "2024-03-01T09:00:00"
    "videoURL": "..."
  },
  "summaries": [
    {
      "id": 23,
      "title": "Standup Intro",
      "summary": "Members discussed...",
      "startTime": "00:09:11,500"
    },
    ...
  ],
  "agenda": [
    {
      "id": 35,
      "fileNumber": "22-0403-S3",
      "itemNumber": 1,
      "orderNumber": 1,
      "title": "Roll Call...",
      "description": "Speakers...",
    },
    ...
  ]
}
```
> Note: The exact fields in the response depend on the `MeetingInfo` model definition in `src/models.py`.

**Response (404 Not Found):**
```json
{
  "detail": "No meetings found"
}
```

**Response (422 Unprocessable Entity):**
```bash
curl -X GET "http://<host>/getMeetingInfo/abc"
```
```json
{
  "detail": [
    {
      "loc": ["path", "meeting_id"],
      "msg": "value is not a valid integer",
      "type": "type_error.integer"
    }
  ]
}
```

### Notes & Limitations

- `meeting_id` must be a valid **integer** — string values will result in a `422` error.
- The database query calls the stored PostgreSQL function `get_meeting_json(%s)`. If that function does not exist or has a schema mismatch, a `400` SQL error will be raised.
- Database connection is configured via the `DB_CONN` environment variable, or constructed from `DB_PASSWORD` if `DB_CONN` is not set.
- CORS is fully open (`allow_origins=["*"]`) — all origins are permitted.
- No authentication is required for this endpoint.

---

## Additional Endpoints

### `GET /getMeetings`

**Description:** Returns a list of all meetings by calling the PostgreSQL function `get_meetings_json()`.

**Response Model:** `MeetingsData`

**Parameters:** None

**Errors:**

| Condition                  | Status | Detail                                |
|----------------------------|--------|---------------------------------------|
| `psycopg.OperationalError` | `503`  | `"Database connection failed: ..."` |
| `psycopg.ProgrammingError` | `400`  | `"SQL error: ..."`                  |
| `psycopg.Error`            | `500`  | `"Database error: ..."`             |
| No results returned        | `404`  | `"No meetings found"`                 |

**Example:**
```bash
curl -X GET "http://<host>/getMeetings" -H "Accept: application/json"
```

**Response (200 OK):**
```json
{
  "meetings": [
    {
      "id": 42,
      "title": "Weekly Standup",
      "date": "2024-03-01T09:00:00"
      "videoURL": "..."
    },
    ...
  ]
}
```

---

### `GET /`

**Description:** Root health-check endpoint. Confirms the API is running.

**Parameters:** None

**Returns:**
```json
{ "message": "Hello World" }
```

---

### `GET /dbTestConnection`

**Description:** Tests whether the API can successfully connect to the PostgreSQL database.

**Parameters:** None

**Returns:**

| Status | Response                                    |
|--------|---------------------------------------------|
| `200`  | `{ "message": "Connection okay" }`          |
| `500`  | `{ "detail": "Unexpected error: <e>" }`     |

**Example:**
```bash
curl -X GET "http://<host>/dbTestConnection"
```
