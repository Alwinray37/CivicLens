# council-pipeline

CLI tool that downloads, transcribes, and processes LA City Council meetings into structured data. It fetches meetings from the LA City Council public portal, downloads video and agenda PDFs, generates transcripts with WhisperX, produces AI summaries via Ollama, and outputs SQL backup files and/or inserts directly into a PostgreSQL database.

## Requirements

- Python 3.11+
- CUDA-capable GPU (required for WhisperX transcription)
- [ffmpeg](https://ffmpeg.org/download.html) installed and on PATH
- [Ollama](https://ollama.com/) running with the required models pulled
- PostgreSQL with the [pgvector](https://github.com/pgvector/pgvector) extension (for DB insertion)
- A [HuggingFace token](https://huggingface.co/settings/tokens) with access to pyannote models

### Ollama Models

The pipeline uses these models by default. Pull them before running:

```bash
ollama pull llama3.1:8b
ollama pull qwen3-embedding:4b
```

## Installation

```bash
cd Models
pip install -e .
```

This installs the `council-pipeline` command.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `PYANNOTE_TOKEN` | Yes | HuggingFace token for speaker diarization |
| `DB_CONN` | No | PostgreSQL connection string (e.g. `postgresql://user:pass@localhost:5431/postgres`) |

Set them in a `.env` file (gitignored) or export them directly:

```bash
export PYANNOTE_TOKEN="hf_your_token_here"
export DB_CONN="postgresql://postgres:password@localhost:5431/postgres"
```

## Configuration

The pipeline reads from `config.yaml` in the current working directory. If not found, defaults are used. You can also pass `--config PATH` to specify a different file.

```yaml
# Directory where SQL backup files are written
output_dir: "output"

# Directory for intermediate files during processing
temp_dir: ".temp"

# Calendar year for fetching meetings with --latest
meeting_year: 2026

# PostgreSQL connection string (can also use DB_CONN env var)
# db_url: "postgresql://postgres:password@localhost:5431/postgres"
```

## Usage

### Initialize the database

Creates all tables, functions, and the pgvector extension. Run this once before processing meetings.

```bash
council-pipeline --init-db
```

Requires `DB_CONN` or `db_url` in config.

### Process the most recent meeting

```bash
council-pipeline --latest
```

This is also the default behavior when no flags are provided:

```bash
council-pipeline
```

### Process a meeting on a specific date

```bash
council-pipeline --date 2026-03-12
```

The year in the date is used automatically to query the correct calendar year.

### Generate SQL backup only (no DB insert)

```bash
council-pipeline --latest --no-db
```

Runs the full pipeline but skips the database insertion step. The SQL backup file is still written to the `output/` directory.

### Use a custom config file

```bash
council-pipeline --latest --config /path/to/config.yaml
```

## Pipeline Stages

The pipeline runs these stages in order:

| Stage | Description |
|---|---|
| **MeetingFetcher** | Queries the LA PrimeGov API for council meetings in the target year |
| **PdfDownloader** | Downloads the meeting agenda PDF |
| **PdfParser** | Extracts agenda items, roll calls, votes, and motions from the PDF |
| **VideoDownloader** | Downloads the meeting audio from the video URL |
| **AudioConverter** | Converts the downloaded M4A audio to MP3 via ffmpeg |
| **TranscriptGen** | Runs WhisperX with speaker diarization to produce a transcript |
| **ChunkGen** | Splits the transcript into chunks and generates embeddings |
| **SummaryGen** | Uses Ollama to generate summaries of the most important events |
| **CombineMeetingData** | Combines agenda, summaries, and chunks into a single JSON |
| **SqlGen** | Generates a SQL backup file in `output/` (always runs) |
| **DbInsert** | Inserts data directly into PostgreSQL (runs if `db_url` is configured) |

## Output

### SQL backup files

Every run produces a file at `output/Meeting_YYYY-MM-DD.sql` containing all INSERT statements for that meeting. These serve as human-readable records and can be applied manually:

```bash
psql -h localhost -p 5431 -U postgres -f output/Meeting_2026-03-12.sql
```

### Database

When `db_url` is configured, the pipeline inserts directly into these tables:

- `Meetings` -- meeting date, video URL, title
- `AgendaItems` -- parsed agenda items with titles, descriptions, file numbers
- `Summaries` -- AI-generated summaries with start times
- `MeetingChunks` -- transcript chunks with vector embeddings (used by the chatbot)

## Docker

When running as part of the CivicLens Docker Compose stack, set `DB_CONN` and `PYANNOTE_TOKEN` in the root `.env` file. The pipeline connects to the `db` service on port 5432 (internal) or 5431 (host-mapped).

## Troubleshooting

| Problem | Fix |
|---|---|
| `ffmpeg is not installed or not found on PATH` | Install ffmpeg and restart your terminal |
| `CUDA is not available` | Check GPU drivers and CUDA toolkit installation |
| `No meetings found` | Verify the meeting year in config or use `--date` with a known date |
| `db_url is not configured` | Set `DB_CONN` env var or add `db_url` to `config.yaml` |
| `Failed to download YouTube video` | Meeting video may not be available yet; try a different date |
