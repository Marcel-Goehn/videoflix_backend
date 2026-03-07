import os
import subprocess

def convert_video(source, quality):
    """
    Converts the uploaded video to the desired quality
    with the help of ffmpeg
    """
    base = os.path.splitext(source)[0]
    new_file_name = f'{base}_{quality}p.mp4'
    cmd = 'ffmpeg -i "{}" -vf scale=-2:{} -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, quality, new_file_name)
    subprocess.run(cmd, shell=True, capture_output=True)


def delete_converted_videos(source, quality):
    """
    Deletes all video files, after the user deletes it via
    the admin dashboard
    """
    base = os.path.splitext(source)[0]
    file_path = f'{base}_{quality}p.mp4'
    if os.path.exists(file_path):
        os.remove(file_path)