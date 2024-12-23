#!/bin/bash

#
# Collects stats about mailing list subscribers.
#
# Run as crontab:
#
# 0 1 * * * /home/crestmlman/scripts/mm2_stats.sh > /tmp/mm2_stats.log

set -xe

LIST_MEMBERS_EXECUTABLE="/opt/mailman/default/bin/list_members"
lists="boost boost-users boost-announce"
current_date=$(date "+%Y-%m-%d")

cd "${HOME}"
mkdir -p mm2_stats
cd mm2_stats

for list in $lists; do
    count=$(${LIST_MEMBERS_EXECUTABLE} "${list}" | wc -l) 
    echo "${current_date} ${count}" >> "${list}.txt"
done
