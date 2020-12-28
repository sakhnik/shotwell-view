#!/usr/bin/env python

"""."""

import sqlite3
from datetime import datetime
import pathlib
import os


QUERY = """
SELECT f.filename, f.exposure_time, e.id, e.name FROM
(SELECT p.filename, p.exposure_time, p.event_id FROM PhotoTable p
UNION
SELECT v.filename, v.exposure_time, v.event_id FROM VideoTable v) AS f
JOIN EventTable e ON f.event_id = e.id
ORDER BY f.exposure_time;
"""

PHOTO_DB = "/home/sakhnik/Pictures/shotwell/data/photo.db"
ROOT = "/home/sakhnik/Pictures2"

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
