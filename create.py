#!/usr/bin/env python

"""Create picture hierarchy based on the information from Shotwell.

Symlinks to the actual files will be put into the directories that
correspond to the descriptive events. The photo/video collection
will be suitable for browsing and viewing with PiGallery2
(https://github.com/bpatrik/PiGallery2).
"""

import common
from events import Events
import sqlite3
import pathlib
import os
import shutil


QUERY = """
SELECT f.filename, f.exposure_time, e.id, e.name FROM
(SELECT p.filename, p.exposure_time, p.event_id FROM PhotoTable p
UNION
SELECT v.filename, v.exposure_time, v.event_id FROM VideoTable v) AS f
JOIN EventTable e ON f.event_id = e.id
ORDER BY f.exposure_time;
"""

# Remove the old view
for f in os.listdir(common.ROOT):
    fpath = pathlib.Path(common.ROOT, f)
    if os.path.islink(fpath):
        os.unlink(fpath)
    elif os.path.isfile(fpath):
        os.remove(fpath)
    else:
        shutil.rmtree(fpath)

events = Events()

with sqlite3.connect(common.PHOTO_DB) as conn:
    c = conn.cursor()
    for (fname, timestamp, eid, ename) in c.execute(QUERY):
        # print(fname, timestamp, eid, ename)
        event_dir = events.get_name(eid)
        dir_path = f"{common.ROOT}/{event_dir}"
        if not event_dir:
            event_dir = common.get_event_dir(timestamp, ename)
            events.set_name(eid, event_dir)
            dir_path = f"{common.ROOT}/{event_dir}"
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        try:
            lname = f"{dir_path}/{common.get_lname(timestamp, fname)}"
            os.symlink(fname, lname)
            # Mark the original timestamp from the database for correct
            # temporal ordering
            os.utime(fname, (timestamp, timestamp), follow_symlinks=False)
            os.utime(lname, (timestamp, timestamp), follow_symlinks=False)
        except Exception as e:
            print(e)

# Dump the assigned event names to a database
events.store()

try:
    os.symlink("/home/sakhnik/Pictures-incoming", f"{common.ROOT}/incoming")
except Exception as e:
    print(e)
