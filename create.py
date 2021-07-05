#!/usr/bin/env python

"""Create picture hierarchy based on the information from Shotwell.

Symlinks to the actual files will be put into the directories that
correspond to the descriptive events. The photo/video collection
will be suitable for browsing and viewing with PiGallery2
(https://github.com/bpatrik/PiGallery2).
"""

import sqlite3
from datetime import datetime
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

PHOTO_DB = "/mnt/pictures/shotwell/data/photo.db"
ROOT = "/home/sakhnik/Pictures2"

# Remove the old view
for f in os.listdir(ROOT):
    fpath = pathlib.Path(ROOT, f)
    if os.path.islink(fpath):
        os.unlink(fpath)
    else:
        shutil.rmtree(fpath)

events = {}  # eid -> path

with sqlite3.connect(PHOTO_DB) as conn:
    c = conn.cursor()
    for (fname, timestamp, eid, ename) in c.execute(QUERY):
        # print(fname, timestamp, eid, ename)
        dir_path = events.get(eid)
        if not dir_path:
            dt = datetime.fromtimestamp(timestamp)
            if ename:
                dir_path = f"{ROOT}/{dt.year}/{dt.year}-{dt.month:02d}-{dt.day:02d} {ename}"
            else:
                dir_path = f"{ROOT}/{dt.year}/{dt.year}-{dt.month:02d}-{dt.day:02d}"
            events[eid] = dir_path
            pathlib.Path(dir_path).mkdir(parents=True, exist_ok=True)
        try:
            os.symlink(fname, f"{dir_path}/{timestamp}_{os.path.basename(fname)}")
        except Exception as e:
            print(e)

try:
    os.symlink("/home/sakhnik/Pictures-incoming", f"{ROOT}/incoming")
except Exception as e:
    print(e)
