# video-to-sqlite

[![PyPI](https://img.shields.io/pypi/v/video-to-sqlite.svg)](https://pypi.org/project/video-to-sqlite/)

Load data about a video file into SQLite

## Installation

Install this tool using `pip`:

    pip install video-to-sqlite

## Usage

To create a SQLite database with metadata about a video, run:

    video-to-sqlite videos.db my_video.mp4

The tool will create two tables: `videos` and `frames`. If `videos.db` already exists, the video will be added to the
`videos` table.

To create the tables with a prefix, use `--prefix prefix`. For example:

    video-to-sqlite videos.db cool_video.mp4 --prefix cool_

This will create tables called `cool_videos` and `cool_frames`.

### Extra processing

Using the library programatically allows extra columns to be added to the database via a callback. Specify the
`callback` argument to `cli.main()`.

The function will be called once per frame in the video. It should accept a numpy ndarray of the frame in question,
and a dict containing metadata for the frame. The callback should return a dict. The dict's keys will be added as
columns to the DB, and values will be the corresponding values for that row.

An example:

```
import video_to_sqlite

def my_callback(frame, metadata):
    has_a_cat_in_it = ai_cat_image_detector(frame)
    
    if metadata['pict_type'] == 'I':  # is this frame a keyframe?
        brightness = get_average_brightness(frame)
    
    return {'cat': has_a_cat_in_it, 'brightness': brightness}

video_to_sqlite.main('my_database.db', 'cool_video.mp4', 'cool_', my_callback)
```

See `callback.py` for a working example.


## video-to-sqlite --help

```
Usage: video-to-sqlite DB_PATH VIDEO_FILE PREFIX

  Load data about frames from a video into SQLite

  Usage example:

      video-to-sqlite videos.db my_video.mp4 my_

  Created tables will be videos and frames

  To create tables called cool_videos, cool_frames use
  --prefix cool_:

      video-to-sqlite videos.db my_video.mp4 --prefix cool_

Options:
  --version            Show the version and exit.
  --prefix TEXT        Prefix to use for the created database tables
  --help               Show this message and exit.

```
