#!/usr/bin/env bash
# Create Mailman lists and bulk HyperKitty archive data for local UI work.
set -euo pipefail

cd "$(dirname "$0")"

DOMAIN="${MAILMAN_DOMAIN:-lists.example.com}"
REST_USER="${MAILMAN_REST_USER:-restadmin}"
REST_PASS="${MAILMAN_REST_PASSWORD:-restpass}"
CORE_URL="${MAILMAN_REST_URL:-http://127.0.0.1:8201}"
LIST_PARTS="${SEED_LISTS:-delegates,paper-reviews,general,dev,announce,cpp,boost,test}"
THREADS="${SEED_THREADS:-35}"
REPLIES="${SEED_REPLIES:-6}"

echo "==> Ensuring Mailman domain: ${DOMAIN}"
curl -sf -X POST -u "${REST_USER}:${REST_PASS}" \
  "${CORE_URL}/3.1/domains" \
  -H "Content-Type: application/json" \
  -d "{\"mail_host\":\"${DOMAIN}\"}" >/dev/null || true

echo "==> Creating mailing lists in Mailman core"
IFS=',' read -ra PARTS <<< "${LIST_PARTS}"
for part in "${PARTS[@]}"; do
  part="$(echo "$part" | xargs)"
  fqdn="${part}@${DOMAIN}"
  if docker compose exec -T mailman-core mailman --run-as-root create -q "${fqdn}" 2>/dev/null; then
    echo "  created ${fqdn}"
  else
    echo "  exists  ${fqdn}"
  fi
done

echo "==> Seeding HyperKitty archives (${THREADS} threads x ${REPLIES} msgs per list)"
docker compose exec -T \
  -e MAILMAN_DOMAIN="${DOMAIN}" \
  -e SEED_LISTS="${LIST_PARTS}" \
  mailman-web sh -c "cd /opt/mailman-web && PYTHONPATH=/opt/mailman-web python /opt/boost-scripts/seed_dev_data.py \
  --domain '${DOMAIN}' \
  --lists '${LIST_PARTS}' \
  --threads '${THREADS}' \
  --replies '${REPLIES}'"

echo "==> Syncing list metadata from Mailman"
docker compose exec -T mailman-web python manage.py mailman_sync

echo "==> Updating search index"
docker compose exec -T mailman-web python manage.py update_index --remove -v 0

echo ""
echo "Ready:"
echo "  Postorius: http://localhost:8400/mailman3/lists/"
echo "  HyperKitty: http://localhost:8400/archives/"
echo "  Example list: http://localhost:8400/archives/list/delegates@${DOMAIN}/"
