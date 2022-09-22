import os

import click
import imageio.v3 as iio
import re
import sqlite_utils
import subprocess

from sqlite_utils.utils import TypeTracker


@click.command()
@click.version_option()
@click.argument(
    'db_path',
    type=click.Path(file_okay=True, dir_okay=False, allow_dash=False),
    required=True,
)
@click.argument(
    'video_file',
    type=click.Path(file_okay=True, dir_okay=False),
)
@click.option(
    '--prefix',
    help='Prefix to use for the created database tables',
    default='',
)
def cli(db_path, video_file, prefix):
    """
    Load data about frames from a video into SQLite

    Usage example:

        video-to-sqlite videos.db my_video.mp4

    Created tables will be named `videos` and `frames`

    To create tables called my_videos, my_frames use --prefix my_:

        video-to-sqlite videos.db my_video.mp4 --prefix my_
    """
    main(db_path, video_file, prefix)


def main(db_path, video_filename, prefix, callback=None):
    """
    Extract info from a video file and write it to an sqlite DB.
    
    By default, the `frames` table contains metadata about each frame.
    To include additional columns, supply a function in the `callback`
    argument.
    
    `callback` is an optional argument for running additional
    processing on each frame of the video.
    If supplied, the function should accept a numpy ndarray of the frame,
    and a dict containing metadata for the given frame, and return a dict.
    Keys in the returned dict will become columns in the database, and values
    will be that column's value for the frame.

    See callback.py for an example.
    """
    db = sqlite_utils.Database(db_path)
    metadata, frames = parse_video(video_filename, callback)
    save_to_db(db, video_filename, metadata, frames, prefix)


def parse_video(video_filename, callback=None):
    process = subprocess.run(['ffprobe', '-hide_banner', video_filename], capture_output=True)
    stderr = process.stderr.decode()

    video_line = [line for line in stderr.splitlines() if line.strip().startswith('Stream #') and 'Video' in line][0].strip()
    video_stats = video_line.split(',')
    codec = video_stats[0].split('Video: ')[1]
    pixel_format = video_stats[1].strip().split('(')[0]
    resolution = video_stats[3].split()[0]
    framerate = video_stats[5].split()[0]

    metadata = {
        'duration': re.search(r'Duration: (\d\d:\d\d:\d\d\.\d\d)', stderr).groups()[0],
        'bitrate': re.search(r'bitrate: (\d+ [kM]?b/s)', stderr).groups()[0],
        'codec': codec,
        'pixel_format': pixel_format,
        'resolution': resolution,
        'framerate': framerate,
    }

    process = subprocess.run(['ffprobe', '-show_frames', video_filename], capture_output=True)
    stdout = process.stdout.decode()
    frames = stdout.split('[/FRAME]')

    processed_frames = []
    for raw_frame in frames:
        lines = raw_frame.split('\n')[1:-1]  # drop the opening and closing "[FRAME]" tags
        frame = {line.split('=')[0]: line.split('=')[1] for line in lines if '=' in line}

        if frame.get('media_type', None) == 'video':

            if frame['pkt_dts'] == 'N/A':
                continue  # last frame doesn't get displayed or something?

            frame['filename'] = os.path.basename(video_filename)
            processed_frames.append(frame)

    if callback:
        for i, (frame, frame_metadata) in enumerate(zip(iio.imiter(video_filename), processed_frames)):
            frame_metadata['frame_no'] = i
            frame_metadata.update(callback(frame, frame_metadata))

    return metadata, processed_frames


def save_to_db(db, video_filename, metadata, frames, prefix):
    data = {
        'filename': video_filename,
        'duration': metadata['duration'],
        'bitrate': metadata['bitrate'],
        'codec': metadata['codec'],
        'pixel_format': metadata['pixel_format'],
        'resolution': metadata['resolution'],
        'framerate': float(metadata['framerate']),
    }

    db[f'{prefix}videos'].insert(
        data,
        pk='filename',
        replace=True,
        alter=True,
    )

    frame_tracker = TypeTracker()
    db[f'{prefix}frames'].insert_all(
        frame_tracker.wrap(frames),
        pk=('frame_no', 'filename'),
        foreign_keys=[
            ('filename', f'{prefix}videos', 'filename'),
        ],
        replace=True,
        alter=True,
    )
    db[f'{prefix}frames'].transform(types=frame_tracker.types)
