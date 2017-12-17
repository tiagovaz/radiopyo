#!/usr/bin/env python

import os
import string
import random
import datetime
import glob
import sys
import shutil
import tokenize
import io
import subprocess
import logging

from pyo import sndinfo

logging.basicConfig(filename='radiopyo.log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

RADIOPYO_PATH = '/home/akj/Downloads/radiopyo/'
PLAYLIST_NO_REPEAT_LEN = len(glob.glob(RADIOPYO_PATH + '*.py')) // 2
QUEUE_HISTORY_FILE = RADIOPYO_PATH + 'queue_history'
CURRENT_SONG_INFO_FILE = RADIOPYO_PATH + 'current_info.txt'


def read_queue_history():
    """A helper function that reads a history queue file, to see what the
    radio has recently played. Keep things interesting by not over-playing
    any tracks.
    """
    try:
        with open(os.path.join(QUEUE_HISTORY_FILE)) as queue_hist:
            last_n = queue_hist.readlines()[-PLAYLIST_NO_REPEAT_LEN:]
    except IOError:
        open(os.path.join(RADIOPYO_PATH, QUEUE_HISTORY_FILE), 'w+').close()
        with open(os.path.join(QUEUE_HISTORY_FILE)) as queue_hist:
            last_n = queue_hist.readlines()[-PLAYLIST_NO_REPEAT_LEN:]
    return [songitem.strip() for songitem in last_n]


def write_queue_history(songname):
    """A helper function that reads a history queue file, to see what the
    radio has recently played. Keep things interesting by not over-playing
    any tracks.
    """
    last_n = read_queue_history()
    last_n.append('{0}'.format(songname))
    last_n = last_n[-PLAYLIST_NO_REPEAT_LEN:]
    with open(os.path.join(QUEUE_HISTORY_FILE), 'w') as queue_hist:
        queue_hist.write('\n'.join(last_n))
    return None


def get_random_song(path=None):
    """The heart of the randomization algorithm. Will not pick a song if
    it has been heard within a certain number of previous songs, and
    will also not choose a song that is being currently rendered.
    """
    # all the songs available, in theory:
    all_songs = set([i for i in glob.glob(path + '*.ogg')])
    # all the songs recently heard:
    last_n = set(read_queue_history())
    # any locked files:
    locked_files = set([i.replace('.lock', '.ogg') \
        for i in glob.glob(path + '*.lock')])
    # choose from the difference set of all the above:
    choices = all_songs.difference(last_n).difference(locked_files)
    song = random.choice(list(choices))
    write_queue_history(song)
    return song


def get_song_info(script_file):
    song_info_dict = {'TITLE': '',
                      'ARTIST': '',
                      'DURATION': ''}
    # TODO: use python import for that
    for l in open(script_file, 'r').readlines():
        if l.split('=')[0].strip() == 'TITLE':
            song_info_dict['TITLE'] = clean_string(nocomment(l.split('=')[1]))
        if l.split('=')[0].strip() == 'ARTIST':
            song_info_dict['ARTIST'] = clean_string(nocomment(l.split('=')[1]))
        if l.split('=')[0].strip() == 'DURATION':
            song_info_dict['DURATION'] = clean_string(os.path.splitext(
                nocomment(l.split('=')[1]))[0])
    return song_info_dict


def nocomment(string):
    return string.split('#')[0]
    #result = []
    #g = tokenize.tokenize(io.BytesIO(string.encode('utf8')).readline)
    #for toknum, tokval, _, _, _ in g:
    #    if toknum != tokenize.COMMENT:
    #        result.append((toknum, tokval))
    #return tokenize.untokenize(result).decode('utf8')


def clean_string(string):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    no_punct = ""
    for char in string:
        if char not in punctuations:
            no_punct = no_punct + char
    return no_punct.strip()


def select_song(path=None):
    # call out to the newer helper function:
    song = get_random_song(path)
    # ices2 needs this
    logger.debug('Selected song: {0}'.format(song))
    song_duration = sndinfo(song)[1]
    now = datetime.datetime.now()
    # tag for update at now + song duration
    removal_date = now + datetime.timedelta(seconds=song_duration)
    song_stamp = '{0}({1}).stamp'.format(song, removal_date)
    open(song_stamp, 'a').close()
    # write music info to a txt which will be available in the web player
    song_info = get_song_info(os.path.splitext(song)[0] + '.py')
    f = open(CURRENT_SONG_INFO_FILE, 'w+')
    current_info = ('<h6>Now playing <em>{0}</em> by {1}</h6> ({2} sec)'
                    .format(song_info['TITLE'], song_info['ARTIST'],
                            song_info['DURATION']))
    f.write(current_info)
    f.close()


def update_song(script_file):
    """Here is where a song first gets rendered to ogg"""
    ogg_file_tmp = ''.join([random.choice(
        string.ascii_letters + string.digits) for n in range(10)]) + '.ogg'
    path = os.path.dirname(script_file)
    basename = os.path.basename(os.path.splitext(script_file)[0])
    full_basename = os.path.join(path, basename)
    ogg_file = full_basename + '.ogg'
    lock_file = full_basename + '.lock'
    stamp_glob = full_basename + '*.stamp'
    stamp_files = [i for i in glob.glob(stamp_glob)]
    update_msg = '# updating {0}; tmp_file: {1} #'.format(
        basename, ogg_file_tmp)
    update_msg = ''.join(['\n', '#' * len(update_msg), '\n', 
                          update_msg, '\n',
                          '#' * len(update_msg), '\n'])
    logger.debug(update_msg)
    # remove other eventual stamps for the same file
    for f in stamp_files:
        logger.debug('Removing {0}'.format(f))
        os.remove(f)
    # lock it to not be played during rendering
    open(lock_file, 'a').close()
    render_cmd = '{0} {1}'.format(script_file, ogg_file_tmp)
    try:
        result = subprocess.check_output(render_cmd,
                                         stderr=subprocess.STDOUT,
                                         shell=True)
    except subprocess.CalledProcessError as process_error:
        logger.debug(process_error.output)
    try:
        song_info = get_song_info(script_file)
        # TODO: use a proper python library for this
        cmd_tags = ('oggz comment -c vorbis -o {0} {1} '
                    'TITLE="{2}" ARTIST="{3}" DURATION="{4}"'
                    .format(ogg_file, ogg_file_tmp,
                            song_info['TITLE'], song_info['ARTIST'],
                            song_info['DURATION']))
        result = subprocess.check_output(cmd_tags,
                                         stderr=subprocess.STDOUT,
                                         shell=True)
        os.remove(ogg_file_tmp)
    except:
        logger.debug('There were errors creating the ogg file'
                     ' for {0}.\n'.format(script_file))
    finally:
        # unlock it
        os.remove(lock_file)


def update_songs(path=None):
    for name in glob.glob(path + '*.stamp'):
        now = datetime.datetime.now()
        scheduled_time = datetime.datetime.strptime(name.split(
            '(')[1].split(')')[0].split('.')[0], '%Y-%m-%d %H:%M:%S')
        if now > scheduled_time:
            script_file = os.path.splitext(name.split('(')[0])[0] + '.py'
            update_song(script_file)
            # avoid generating same file twice, go to a new loop
            break


def update_all_songs(path=None):
    all_songs = [i for i in glob.glob(path + '*.ogg')]
    import string
    for name in glob.glob(path + '*.py'):
        if name.replace('.py', '.ogg') not in all_songs:
            update_song(name)


def main():
    cmdargs = sys.argv
    if len(cmdargs) == 1:
        select_song(RADIOPYO_PATH)
    else:    
        if cmdargs[1] == 'update':
            update_songs(RADIOPYO_PATH)
        elif cmdargs[1] == 'update_song':
            update_song(cmdargs[2])
        elif cmdargs[1] == 'update_all':
            update_all_songs(RADIOPYO_PATH)

if __name__ == '__main__':
    main()
