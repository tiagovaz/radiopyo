import os
import glob
import json
import argparse

from typing import NoReturn

from radio_pyo import get_song_info


def generate_songs(src: str, output: str, format: str, force: bool, generate_metadata: bool) -> NoReturn:

    all_songs = glob.glob(src + '*.py')
    generated_songs = glob.glob(output + f'/*.{format}')
    generated_songs_names = [os.path.basename(song).split('.')[0] for song in generated_songs]

    songs_metadata = []

    for script in all_songs:
        song_name = os.path.basename(script).split('.')[0]
        outfile_path= f'{output}/{song_name}.{format}'

        new_metadata = get_song_info(script_file=script)
        new_metadata['PATH'] = outfile_path
        songs_metadata.append(new_metadata)

        if force or song_name not in generated_songs_names:
            os.system(f"python {script} {outfile_path}")

    if generate_metadata:
        var_content = f'var songsMetadata = {json.dumps(songs_metadata)};'
        with open(f'{output}/songs_metadata.js', 'w', encoding='utf-8') as f:
            f.write(var_content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate files from song generating scripts')
    parser.add_argument('-s', '--src', default='./songs_scripts/', help='Source folder containing all scripts')
    parser.add_argument('-o', '--output', default='./songs/', help='Output folder to store all songs')
    parser.add_argument('-f', '--format', default='ogg', help='Output format')
    parser.add_argument('--force', action='store_true', default=False, help='regenerate all songs')
    parser.add_argument('--nometadata', action='store_true', default=False, help='do not regenerate the metadata file')

    args = parser.parse_args()
    generate_songs(args.src, args.output, args.format, args.force, not args.nometadata)
