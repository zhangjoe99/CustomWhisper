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

  in_file = args.filename
  out_file = "clip_" + in_file

  # get duration of in_file
  get_duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', in_file]
  
  # build bash cmd
  process = subprocess.Popen(get_duration_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
  # collect cmd output
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
      seg_file_name = out_file.replace('clip_', 'clip_{}-{}_'.format(t1, t2))
      
      # build split_video bash cmd: change -n to -y to automatically overwrite existing files
      split_video_cmd = None
      if (args.over_write):
        split_video_cmd = ['ffmpeg', '-y', '-ss', str(t1), '-i', in_file, '-c', 'copy', '-t', str(t2), seg_file_name]
        # resulting cmd: ffmpeg -y -ss t1 -i in_file -c copy -t t2 seg_file_name
      else:
        split_video_cmd = ['ffmpeg', '-n', '-ss', str(t1), '-i', in_file, '-c', 'copy', '-t', str(t2), seg_file_name]
        # resulting cmd: ffmpeg -n -ss t1 -i in_file -c copy -t t2 seg_file_name
      
      # run cmd
      proc = subprocess.Popen(split_video_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
      
      # collect output
      out, err = proc.communicate()
      print('CMD OUTPUT:\n{}\nCMD ERROR:\n{}\n'.format(out, err))

# so main() isn't executed if file is imported
if __name__ == "__main__":
    # remove first script name argument
    main(sys.argv[1:])
