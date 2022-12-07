import os
import sys
import subprocess
import math
import argparse

def argument_handler():
  parser = argparse.ArgumentParser(prog="splitVideo", description="splits input video into 5s clips")
  parser.add_argument('filename', help="name of input file to split")
  parser.add_argument('-o', '--overwrite', action="store_true", dest='over_write', help="overwrite existing files with same name")
  return parser.parse_args()


def main(argv):

  # get passed in arguments 
  args = argument_handler()

  overwrite = '-n'
  if (args.over_write):
    overwrite = '-y'

  in_file = args.filename

  # make copy of in_file with forced keyframes every ~1s (assuming in_file is 30fps)
  forced_keyframe_file = in_file.replace('.', '_forced_key_frames.')
  print('making temporary working copy of {} with ~1s forced key frames...'.format(in_file))
  # build bash cmd
  split_video_cmd = ['ffmpeg', '-i', in_file, '-g', '30', overwrite, forced_keyframe_file]
  # excecute cmd
  process = subprocess.Popen(split_video_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  # collect, print cmd output
  out, err = process.communicate()
  #print('CMD OUTPUT:\n{}\nCMD ERROR:\n{}\n'.format(out, err))

  ## note: print key frames of file with cmd: ffprobe -loglevel error -select_streams v:0 -show_entries packet=pts_time,flags -of csv=print_section=0 example-video_forced_key_frames.mkv | awk -F',' '/K/ {print $1}'

  print('splitting {} into 5s interval clips...'.format(in_file))
  
  # get duration of in_file
  get_duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', in_file]
  process = subprocess.Popen(get_duration_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  out, err = process.communicate()
  length = math.floor(float(out)) # length (s) of in_file
 
  # iterate through clips
  i = 0 # clip start counter
  k = 0 # loop counter (also clip end counter)
  while k < length:
    # keep start time 0 and iterate end time by 1s until 5s reached
    if (k < 5):
        k += 1
    else: # afterwards begin iterating both start/end times by 1s
        i += 1
        k += 1

    # format output name of clip, based on start/end times
    clip_file_name = forced_keyframe_file.replace('.', 'clip_{}-{}.'.format(i, k))

    # build split_video bash cmd
    split_video_cmd = ['ffmpeg', '-i', forced_keyframe_file, '-ss', str(i), '-to', str(k), overwrite, clip_file_name]
    # resulting cmd: ffmpeg [in_file] -ss [i] -to [k] -c copy -[y/n] clip_file_name

    # run cmd
    proc = subprocess.Popen(split_video_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    # collect, print output
    out, err = proc.communicate()
    #print('CMD OUTPUT:\n{}\nCMD ERROR:\n{}\n'.format(out, err))

  print('removing temporary working file: {}'.format(forced_keyframe_file))
  remove_fkf_file = ['rm', forced_keyframe_file]
  proc = subprocess.Popen(remove_fkf_file, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  out, err = proc.communicate()
  #print('CMD OUTPUT:\n{}\nCMD ERROR:\n{}\n'.format(out, err))

# so main() isn't executed if file is imported
if __name__ == "__main__":
    # remove first script name argument
    main(sys.argv[1:])
