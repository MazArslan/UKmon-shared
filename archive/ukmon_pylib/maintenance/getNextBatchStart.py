# Copyright (C) 2018-2023 Mark McIntyre
#
# script to get next batch start time in a format compatible with at
#

from RMS.CaptureDuration import captureDuration
import datetime
import sys
from crontab import CronTab


offset = 90
batchname = 'nightlyJob'
if len(sys.argv) > 1:
    offset = int(sys.argv[1])
if len(sys.argv) > 2:
    batchname = sys.argv[2]

st, dur=captureDuration(51.88,-1.31,80) 
if st is True:
    # the batch too too long to run so just quit
    exit(0)

dawn = st + datetime.timedelta(seconds=dur)
starttime = dawn + datetime.timedelta(minutes=offset)
print('Setting batch start time to', starttime.strftime('%H:%M'))

cron = CronTab(user=True)
iter=cron.find_command(batchname)
for i in iter:
    if i.is_enabled():
        i.hour.on(starttime.hour)
        i.minute.on(starttime.minute)
cron.write()
