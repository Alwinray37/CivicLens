#!/bin/sh
set -eu
: "${PGHOST:=localhost}"; : "${PGPORT:=5432}"; : "${PGUSER:=postgres}"
# Restores to the DB name inside the dump; will CREATE DATABASE.
tmp="$(mktemp)"
base64 -d > "$tmp" <<'B64'

B64
pg_restore --no-owner --no-privileges --create -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$tmp"
rm -f "$tmp"
echo "Restore complete."
