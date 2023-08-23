import datetime
import os

PHOTO_DB = "/mnt/pictures/shotwell/data/photo.db"
ROOT = "/home/sakhnik/Pictures2"


def get_event_dir(timestamp, ename):
    dt = datetime.datetime.fromtimestamp(timestamp)
    dir_prefix = f"{dt.year}/{dt.year}-{dt.month:02d}-{dt.day:02d}"
    return dir_prefix if not ename else f"{dir_prefix} {ename}"


def get_lname(timestamp, fname):
    return f"{timestamp}_{os.path.basename(fname)}"
