#!/usr/bin/env python

import common
import datetime
from events import Events
import os
import shutil
import sqlite3
import urllib.parse


events = Events()
now = datetime.datetime.now()

daily_dir = f"{common.ROOT}/this_day"
try:
    shutil.rmtree(daily_dir)
except FileNotFoundError:
    ...
os.mkdir(daily_dir)


def write_year(year, conn, fout):
    fout.write(f"# {year}\n\n")
    # Create a datetime object for the start and end of the day
    start_of_day = datetime.datetime(year, now.month, now.day, 0, 0, 0)
    end_of_day = datetime.datetime(year, now.month, now.day, 23, 59, 59)
    # Convert datetime objects to Unix timestamps
    start_timestamp = int(start_of_day.timestamp())
    end_timestamp = int(end_of_day.timestamp())

    # Query photos for the target date
    query = """
        SELECT f.filename, f.exposure_time, e.id, e.name FROM PhotoTable f
        JOIN EventTable e ON f.event_id = e.id
        WHERE f.exposure_time >= ? AND f.exposure_time <= ?
        ORDER BY RANDOM()
        LIMIT 3
    """
    cursor = conn.cursor()
    cursor.execute(query, (start_timestamp, end_timestamp))
    photos = cursor.fetchall()
    for fname, timestamp, eid, ename in photos:
        event_dir = events.get_name(eid)
        event_url = urllib.parse.quote(event_dir)
        event_url_noslash = urllib.parse.quote(event_dir, safe='')
        lname = common.get_lname(timestamp, fname)
        lname_url = urllib.parse.quote(lname)
        pic_url = f"{event_url}/{lname_url}"
        img_path = f"/pgapi/gallery/content/{pic_url}/thumbnail/240"
        link_url = f"/gallery/{event_url_noslash}?p={lname_url}"
        img = f"[![{ename}]({img_path})]({link_url})"
        fout.write(f"{img}\n")
    fout.write("\n")


with open(f"{daily_dir}/{int(now.timestamp())}.md", "w") as fout:
    with sqlite3.connect(common.PHOTO_DB) as conn:
        for year in range(now.year - 1, 2000, -1):
            write_year(year, conn, fout)
