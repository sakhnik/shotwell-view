#!/usr/bin/env python

import common
from datetime import datetime
from events import Events
import os
import shutil
import sqlite3
import typing
import urllib.parse


daily_dir = f"{common.ROOT}/this_day"


class Daily:
    def __init__(self):
        self.events = Events()
        self.now = datetime.now()

    def get_years_ago(self, n: int) -> str:
        """Get Ukrainian translation for 'n years ago'."""
        ones = n % 10
        tens = n / 10 % 10
        if ones == 1 and tens != 1:
            return f"{n} рік тому"
        if ones >= 2 and ones <= 4 and tens != 1:
            return f"{n} роки тому"
        return f"{n} років тому"

    def write_year(self, year: int, conn: sqlite3.Connection,
                   fout: typing.TextIO):
        """Write photos and videos for a given year."""
        # Create a datetime object for the start and end of the day
        start_of_day = datetime(year, self.now.month, self.now.day, 0, 0, 0)
        end_of_day = datetime(year, self.now.month, self.now.day, 23, 59, 59)
        # Convert datetime objects to Unix timestamps
        start_timestamp = int(start_of_day.timestamp())
        end_timestamp = int(end_of_day.timestamp())

        conn.execute("""CREATE TEMP VIEW IF NOT EXISTS PhotosAndVideos AS
SELECT p.filename, p.exposure_time, p.event_id FROM PhotoTable p
UNION
SELECT v.filename, v.exposure_time, v.event_id FROM VideoTable v
                     """)
        # Query photos for the target date
        query = """
SELECT * FROM
    (SELECT f.filename, f.exposure_time, e.id, e.name FROM PhotosAndVideos AS f
    JOIN EventTable e ON f.event_id = e.id
    WHERE f.exposure_time >= ? AND f.exposure_time <= ?
    ORDER BY RANDOM()
    LIMIT 10)
ORDER BY id, exposure_time
        """
        cursor = conn.cursor()
        cursor.execute(query, (start_timestamp, end_timestamp))
        photos = cursor.fetchall()
        if not photos:
            return
        years_ago = self.get_years_ago(self.now.year - year)
        fout.write(f"## {year} ({years_ago})\n\n")
        prev_eid = -1
        for fname, timestamp, eid, ename in photos:
            # Output event name when changes
            if eid != prev_eid:
                prev_eid = eid
                fout.write(f"### {ename}\n")
            event_dir = self.events.get_name(eid)
            event_url = urllib.parse.quote(event_dir)
            event_url_noslash = urllib.parse.quote(event_dir, safe='')
            lname = common.get_lname(timestamp, fname)
            lname_url = urllib.parse.quote(lname)
            pic_url = f"{event_url}/{lname_url}"
            img_path = f"/pgapi/gallery/content/{pic_url}/thumbnail/240"
            link_url = f"/gallery/{event_url_noslash}?p={lname_url}"
            img = f"[![{lname}]({img_path})]({link_url})"
            fout.write(f"{img}\n")
        fout.write("\n")

    def create(self):
        """Create a report of this day in past years."""
        try:
            shutil.rmtree(daily_dir)
        except FileNotFoundError:
            ...
        os.mkdir(daily_dir)

        with open(f"{daily_dir}/{int(self.now.timestamp())}.md", "w") as fout:
            fout.write(f'# {self.now.date()}\n')
            fout.write("Цей день в історії\n\n")
            with sqlite3.connect(common.PHOTO_DB) as conn:
                for year in range(self.now.year - 1, 2000, -1):
                    self.write_year(year, conn, fout)


if __name__ == "__main__":
    Daily().create()
