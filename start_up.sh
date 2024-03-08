#!/bin/sh
echo "$CRON_REPAIR python /PalRepair/repair.py >> /var/log/repair.log 2>&1" > /etc/crontabs/root
cat /etc/crontabs/root
python /PalRepair/repair.py
crond -f

#keep
/bin/sh