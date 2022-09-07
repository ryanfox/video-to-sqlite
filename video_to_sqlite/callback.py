import sys

from video_to_sqlite import cli


def process(frame):
    """
    An example of using a callback to add custom columns to a video-to-sqlite db.
    Add the highest, lowest, and mean value of the frame to the row.

    :param frame: a numpy ndarray of the video frame
    :return: a dict, where keys will be column names and values the cell contents in the db
    """
    maximum = frame.max()
    minimum = frame.min()
    mean = frame.mean()

    return {
        'max': maximum,
        'min': minimum,
        'mean': mean,
    }


if __name__ == '__main__':
    """
    Usage: python callback.py <db file> <video file>
    Call `cli.main()` with the database file, video file, prefix, and callback function
    """
    cli.main(sys.argv[1], sys.argv[2], callback=process)
