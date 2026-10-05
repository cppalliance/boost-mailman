#!/usr/bin/env bash
# Additive, richer archive seed (ported from wg21-mailman). Creates extra lists
# with nested threads, votes, tags, favorites, attachments and a demo user.
# Safe to re-run; never deletes existing lists, users or messages.
set -euo pipefail

cd "$(dirname "$0")"

DOMAIN="${MAILMAN_DOMAIN:-lists.example.com}"
LIST_PARTS="${SEED_RICH_LISTS:-boost-users,boost-interest,boost-announce,boost-testing,boost-docs,boost-steering,boost-langbinding}"
THREADS="${SEED_THREADS:-12}"
REPLIES="${SEED_REPLIES:-5}"

echo "==> Creating mailing lists in Mailman core"
IFS=',' read -ra PARTS <<< "${LIST_PARTS}"
for part in "${PARTS[@]}"; do
  part="$(echo "$part" | xargs)"
  fqdn="${part}@${DOMAIN}"
  if create_output="$(docker compose exec -T mailman-core mailman --run-as-root create -q "${fqdn}" 2>&1)"; then
    echo "  created ${fqdn}"
  elif [[ "${create_output}" == *"already exists"* ]]; then
    echo "  exists  ${fqdn}"
  else
    echo "  FAILED  ${fqdn}:" >&2
    echo "${create_output}" >&2
    exit 1
  fi
done

echo "==> Seeding HyperKitty archives (${THREADS} threads x ${REPLIES} msgs per list)"
docker compose exec -T mailman-web sh -c "cd /opt/mailman-web && PYTHONPATH=/opt/mailman-web python /opt/boost-scripts/seed_wg21_data.py \
  --domain '${DOMAIN}' \
  --lists '${LIST_PARTS}' \
  --threads '${THREADS}' \
  --replies '${REPLIES}'"

echo "==> Syncing list metadata from Mailman"
docker compose exec -T mailman-web python manage.py mailman_sync

echo "==> Updating search index"
docker compose exec -T mailman-web python manage.py update_index -v 0

echo ""
echo "Ready:"
echo "  Postorius:  http://localhost:8400/mailman3/lists/"
echo "  HyperKitty: http://localhost:8400/archives/"
echo "  Demo login: demo / demo  (Favorites, Posted, votes, last-views)"
