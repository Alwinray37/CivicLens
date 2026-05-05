#!/usr/bin/env bash
# Wrap council-pipeline so it only does work when the LA PrimeGov API has a
# meeting newer than what's already in the database. Cheap to invoke (one
# HTTP GET + one SQL SELECT), so this is safe to call on a tight cron cadence.
#
# Usage: run_if_new.sh <env_file>
#
# <env_file> is sourced for DB_CONN and PYANNOTE_TOKEN. Same file format
# docker compose --env-file expects (KEY=VALUE per line).
#
# Optional overrides (set in the cron entry or in the env file):
#   COUNCIL_PIPELINE_VENV   venv where `council-pipeline` is installed.
#                           default: /home/overseer/civiclens-pipeline/.venv
#   COUNCIL_PIPELINE_DIR    Models/ directory used as cwd for the pipeline.
#                           default: /home/overseer/test/CivicLens/Models
#   COUNCIL_PIPELINE_LOGDIR where logs are written.
#                           default: /home/overseer/civiclens-pipeline/logs
#   COUNCIL_DB_CONTAINER    docker container name of the postgres service.
#                           Used to rewrite DB_CONN's hostname (which is the
#                           internal compose name `db`, unreachable from the
#                           host) to the container's bridge IP.
#                           default: civiclens-dev-db-1
#
# ─── One-time host bring-up ───────────────────────────────────────────────
#   sudo apt install -y ffmpeg python3-venv python3-pip
#   python3 -m venv /home/overseer/civiclens-pipeline/.venv
#   /home/overseer/civiclens-pipeline/.venv/bin/pip install \
#       -e /home/overseer/test/CivicLens/Models
#   # initialize the schema once per DB:
#   set -a; . /home/overseer/config/civiclens-dev.env; set +a
#   cd /home/overseer/test/CivicLens/Models && \
#       /home/overseer/civiclens-pipeline/.venv/bin/council-pipeline --init-db
#
# ─── Cron entry (after bring-up) ──────────────────────────────────────────
# Chain dev + prod sequentially in one entry. The wrapper's flock means
# back-to-back invocations against the same lock file run in series; the `;`
# (rather than `&&`) ensures prod still runs if dev fails.
#
#   0 */2 * * * /home/overseer/test/CivicLens/Models/scripts/run_if_new.sh \
#       /home/overseer/config/civiclens-dev.env; \
#     /home/overseer/test/CivicLens/Models/scripts/run_if_new.sh \
#       /home/overseer/config/civiclens-prod.env

set -euo pipefail

env_file="${1:?usage: run_if_new.sh <env_file>}"
[[ -r "$env_file" ]] || { echo "env file not readable: $env_file" >&2; exit 2; }

: "${COUNCIL_PIPELINE_VENV:=/home/overseer/civiclens-pipeline/.venv}"
: "${COUNCIL_PIPELINE_DIR:=/home/overseer/test/CivicLens/Models}"
: "${COUNCIL_PIPELINE_LOGDIR:=/home/overseer/civiclens-pipeline/logs}"
: "${COUNCIL_DB_CONTAINER:=civiclens-dev-db-1}"

mkdir -p "$COUNCIL_PIPELINE_LOGDIR"
log_file="$COUNCIL_PIPELINE_LOGDIR/run_if_new.log"
log() { printf '[%s] %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$*" >> "$log_file"; }

exec 9> "$COUNCIL_PIPELINE_LOGDIR/.run_if_new.lock"
if ! flock -n 9; then
    log "skip: previous run still in progress"
    exit 0
fi

set -a
# shellcheck disable=SC1090
. "$env_file"
set +a

: "${DB_CONN:?DB_CONN not set in $env_file}"
: "${PYANNOTE_TOKEN:?PYANNOTE_TOKEN not set in $env_file}"

[[ -x "$COUNCIL_PIPELINE_VENV/bin/python" ]] || {
    log "venv missing at $COUNCIL_PIPELINE_VENV — run host bring-up steps"
    exit 3
}

# council-pipeline shells out to `whisperx` without an absolute path, so the
# venv's bin/ has to be on PATH for the subprocess.
export PATH="$COUNCIL_PIPELINE_VENV/bin:$PATH"

# DB_CONN in the env file uses the compose-internal hostname `db`, which the
# host can't resolve. Rewrite to the container's current bridge IP. Container
# IPs are stable across runs unless the network is recreated.
db_ip=$(docker inspect -f \
    '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{"\n"}}{{end}}' \
    "$COUNCIL_DB_CONTAINER" 2>/dev/null | head -n1)
if [[ -z "$db_ip" ]]; then
    log "could not resolve IP for container $COUNCIL_DB_CONTAINER"
    exit 4
fi
DB_CONN="${DB_CONN//@db:/@${db_ip}:}"
export DB_CONN

cd "$COUNCIL_PIPELINE_DIR"

# Precheck: returns rc=0 when there's a newer meeting, rc=100 when DB is
# already current, anything else is an error.
set +e
precheck=$("$COUNCIL_PIPELINE_VENV/bin/python" - <<'PY' 2>&1
import os, sys, datetime, requests
from sqlalchemy import create_engine, text

year = datetime.date.today().year
url = f"https://lacity.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={year}"
resp = requests.get(url, timeout=30)
resp.raise_for_status()

valid = [
    m for m in resp.json()
    if m.get("meetingTypeId") == 1
    and "SAP" not in m.get("title", "")
    and m.get("videoUrl")
    and any(d.get("templateName") == "Agenda" for d in (m.get("documentList") or []))
]
if not valid:
    print("api: no valid meetings")
    sys.exit(100)

api_latest = max(m["dateTime"][:10] for m in valid)

eng = create_engine(os.environ["DB_CONN"])
with eng.connect() as c:
    db_latest = c.execute(text('SELECT MAX("Date") FROM public."Meetings"')).scalar()
db_str = db_latest.isoformat() if db_latest else "none"

print(f"api={api_latest} db={db_str}")
sys.exit(0 if (db_latest is None or api_latest > db_latest.isoformat()) else 100)
PY
)
rc=$?
set -e

case "$rc" in
    0)
        log "new meeting available ($precheck) — running pipeline"
        run_log="$COUNCIL_PIPELINE_LOGDIR/run-$(date -u +%Y%m%dT%H%M%SZ).log"
        if "$COUNCIL_PIPELINE_VENV/bin/council-pipeline" --latest \
                >> "$run_log" 2>&1; then
            log "pipeline ok ($run_log)"
        else
            prc=$?
            log "pipeline FAILED rc=$prc ($run_log)"
            exit "$prc"
        fi
        ;;
    100)
        log "no new meeting ($precheck)"
        ;;
    *)
        log "precheck error rc=$rc: $precheck"
        exit "$rc"
        ;;
esac
