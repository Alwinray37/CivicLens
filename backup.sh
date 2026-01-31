# make a self-contained creator script
ts="$(date -u +%Y%m%dT%H%M%SZ)"
dump="civiclens_${ts}.dump"
pg_dump -F c -d "$PGDATABASE" -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -f "$dump"

b64=$(base64 -w0 "$dump")
cat > "create_civiclens_db_${ts}.sh" <<'EOS'
#!/bin/sh
set -eu
: "${PGHOST:=localhost}"; : "${PGPORT:=5432}"; : "${PGUSER:=postgres}"
# Restores to the DB name inside the dump; will CREATE DATABASE.
tmp="$(mktemp)"
base64 -d > "$tmp" <<'B64'
__EMBEDDED_DUMP_BASE64__
B64
pg_restore --no-owner --no-privileges --create -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" "$tmp"
rm -f "$tmp"
echo "Restore complete."
EOS
# inject data
sed -i "s|__EMBEDDED_DUMP_BASE64__|$b64|g" "create_civiclens_db_${ts}.sh"
chmod +x "create_civiclens_db_${ts}.sh"
rm -f "$dump"

git add "create_civiclens_db_${ts}.sh"
git commit -m "creator script: $ts" && git push
