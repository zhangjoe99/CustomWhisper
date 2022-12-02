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

length = math.floor(float(out))
times = []
for i in range(min(length,5)):
  times.append([0,i+1])


if length >5:
  for i in range(1,length-5+1):
    times.append([i,i+5])

for t1,t2 in times:
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
