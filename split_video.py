import os
import subprocess
import math

in_file = "example-video.mkv"
out_file = "split-vid.mkv"

# get duration of in_file
get_duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', in_file]
# build bash cmd
process = subprocess.Popen(get_duration_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
# collect output
out, err = process.communicate()

# video length (s)
length = math.floor(float(out))

# iterate through segments
i = 0 # while loop counter
k = 1 # counter for first sub-5s segments
while k <= length:
    t1 = i # segment start time
    t2 = i + 5 # segment end time
    # keep start time 0 and iterate end time by 1s until 5s reached
    if (k < 5):
        t2 = k
        k += 1
    else: # afterwards begin iterating start time by 1s
        i += 1
        k += 1

    # format out_file name for each clip, based on start/end times
    seg_file_name = out_file.replace('.mkv', '{}-{}.mkv'.format(t1, t2))
    # build split_video bash cmd: change -n to -y to automatically overwrite existing files
    # resulting cmd: ffmpeg -y -ss t1 -i in_file -c copy -t t2 seg_file_name
    split_video_cmd = ['ffmpeg', '-n', '-ss', str(t1), '-i', in_file, '-c', 'copy', '-t', str(t2), seg_file_name]
    # run cmd
    proc = subprocess.Popen(split_video_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # collect output
    out, err = proc.communicate()
    print('cmd output: {} \n error: {}'.format(out, err))
