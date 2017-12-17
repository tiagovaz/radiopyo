#!/usr/bin/python2

import os
import random
import datetime
import glob
import sys
import shutil
import tokenize
import io

from pyo import sndinfo

RADIOPYO_PATH = '/xxxx/'
PLAYLIST_NO_REPEAT_LEN = 15


def read_queue_history():
    """A helper function that reads a history queue file, to see what the
    radio has recently played. Keep things interesting by not over-playing
    any tracks.
    """
    try:
        with open(os.path.join(RADIOPYO_PATH, 'queue_history')) as queue_hist:
            last_n = queue_hist.readlines()[-PLAYLIST_NO_REPEAT_LEN:]
    except IOError:
        open(os.path.join(RADIOPYO_PATH, 'queue_history'), 'w+').close()
        with open(os.path.join(RADIOPYO_PATH, 'queue_history')) as queue_hist:
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
    with open(os.path.join(RADIOPYO_PATH, 'queue_history'), 'w') as queue_hist:
        queue_hist.write('\n'.join(last_n))
    return None


def get_random_song(path):
    """The heart of the randomization algorithm. Will not pick a song if
    any of the following are True:

    1) The song is stamped, and thus played and in queue to be deleted;
    2) The song is locked, and being rendered.
    3) The song has been heard within the last 15 songs, provided there
       are 15 songs in the history to review. The logic waits to ensure
       that at least 5 songs are rendered, as a sanity check.
    """
    while True:
        all_songs = [i for i in glob.glob(path + '*.ogg')]
        song = random.choice(all_songs)
        last_n = read_queue_history()
        stamp_files = [
            i for i in glob.glob(os.path.splitext(song)[0] + '*.stamp')]
        locked_files = [
            i for i in glob.glob(os.path.splitext(song)[0] + '.lock')]
        if ((len(all_songs) >= PLAYLIST_NO_REPEAT_LEN * 2
                and song in last_n)
                or stamp_files or locked_files):
            continue    
        else:
            break
    write_queue_history(song)
    return song


def select_song(path=None):
    song = get_random_song(path)
    # ices2 needs this
    print(song)
    song_duration = sndinfo(song)[1]
    now = datetime.datetime.now()
    # tag for update at now + song duration
    removal_date = now + datetime.timedelta(seconds=song_duration)
    song_stamp = '{0}({1}).stamp'.format(song, removal_date)
    open(song_stamp, 'a').close()
    # write music info to a txt which will be available in the web player
    song_info = get_song_info(os.path.splitext(song)[0] + '.py')
    f = open('/var/www/html/radiopyo/current_info.txt', 'w')
    current_info = ('<h6>Now playing <em>{0}</em> by {1}</h6> ({2} sec)'
                    .format(song_info['TITLE'], song_info['ARTIST'],
                            song_info['DURATION']))
    f.write(current_info)
    f.close()


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
    result = []
    g = tokenize.tokenize(io.BytesIO(string.encode('utf8')).readline)
    for toknum, tokval, _, _, _ in g:
        if toknum != tokenize.COMMENT:
            result.append((toknum, tokval))
    return tokenize.untokenize(result).decode('utf8')


def clean_string(string):
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    no_punct = ""
    for char in string:
        if char not in punctuations:
            no_punct = no_punct + char
    return no_punct.strip()


def update_song(script_file, ogg_file_tmp):
    """Here is where a song first gets rendered to ogg"""
    
    path = os.path.dirname(script_file)
    basename = os.path.basename(os.path.splitext(script_file)[0])
    full_basename = os.path.join(path, basename)
    ogg_file = full_basename + '.ogg'
    lock_file = full_basename + '.lock'
    stamp_glob = full_basename + '*.stamp'
    stamp_files = [i for i in glob.glob(stamp_glob)]
    # remove other eventual stamps for the same file
    for f in stamp_files:
        print('Removing {0}'.format(f))
        os.remove(f)
    # lock it to not be played during rendering
    open(lock_file, 'a').close()
    render_cmd = '{0} {1}'.format(script_file, ogg_file_tmp)
    os.system(render_cmd)
    song_info = get_song_info(script_file)
    # TODO: use a proper python library for this
    cmd_tags = ('oggz comment -c vorbis -o {0} {1} '
                'TITLE="{2}" ARTIST="{3}" DURATION="{4}"'
                .format(ogg_file, ogg_file_tmp,
                        song_info['TITLE'], song_info['ARTIST'],
                        song_info['DURATION']))
    os.system(cmd_tags)
    os.remove(ogg_file_tmp)
    # unlock it
    os.remove(lock_file)


def update_songs(path=None, ogg_file_tmp=None):
    for name in glob.glob(path + '*.stamp'):
        now = datetime.datetime.now()
        scheduled_time = datetime.datetime.strptime(name.split(
            '(')[1].split(')')[0].split('.')[0], '%Y-%m-%d %H:%M:%S')
        if now > scheduled_time:
            script_file = os.path.splitext(name.split('(')[0])[0] + '.py'
            update_song(script_file, ogg_file_tmp)
            break  # avoid generating same file twice, go to a new loop


def update_all_songs(path=None, tmp_filename=None):
    for name in glob.glob(path + '*.py'):
        update_song(name, tmp_filename)


def main():
    cmdargs = sys.argv
    if len(cmdargs) == 1:
        select_song(RADIOPYO_PATH)
    else:
        import string
        tmp_filename = ''.join([random.choice(
            string.ascii_letters + string.digits) for n in range(10)]) \
            + '.ogg'
        if cmdargs[1] == 'update':
            update_songs(RADIOPYO_PATH, tmp_filename)
        elif cmdargs[1] == 'update_all':
            update_all_songs(RADIOPYO_PATH, tmp_filename)
        elif cmdargs[1] == 'update_song':
            update_song(cmdargs[2], tmp_filename)

if __name__ == '__main__':
    main()
