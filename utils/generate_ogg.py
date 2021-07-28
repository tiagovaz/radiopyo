import glob
import argparse
from typing import NoReturn
import os

def generate_songs(src: str, output: str, format: str, force: bool) -> NoReturn:

    all_songs = glob.glob(src + '*.py')
    generated_songs = glob.glob(output + f'*.{format}')
    generated_songs = [os.path.basename(song).split('.')[0] for song in generated_songs]

    for script in all_songs:
        song_name = os.path.basename(script).split('.')[0]
        if song_name != '__init__' and (force or song_name not in generated_songs):
            os.system(f"python {script} {output}/{song_name}.{format}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate files from song generating scripts')
    parser.add_argument('-s', '--src', default='./songs_scripts/', help='Source folder containing all scripts')
    parser.add_argument('-o', '--output', default='./website/assets/songs/', help='Output folder to store all songs')
    parser.add_argument('-f', '--format', default='ogg', help='Output format')
    parser.add_argument('--force', action='store_true', default=False, help='regenerate all songs')

    args = parser.parse_args()
    generate_songs(args.src, args.output, args.format, args.force)