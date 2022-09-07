from setuptools import setup
import os

VERSION = '0.0.1'


def get_long_description():
    with open(
       os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
       encoding="utf8",
    ) as fp:
       return fp.read()

setup(
    name='video-to-sqlite',
    description='Load data about a video file into SQLite',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Ryan Fox',
    url='https://github.com/ryanfox/video-to-sqlite',
    project_urls={
        'Issues': 'https://github.com/ryanfox/video-to-sqlite/issues',
    },
    license='ACSL v1.4 (https://anticapitalist.software)',
    version=VERSION,
    packages=['video_to_sqlite'],
    entry_points="""
        [console_scripts]
        video-to-sqlite=video_to_sqlite.cli:cli
    """,
    install_requires=['click', 'sqlite-utils', 'imageio[ffmpeg]'],
    python_requires='>=3.7',
)
