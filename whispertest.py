import whisper
from stable_whisper import modify_model

model = whisper.load_model('base')
modify_model(model)
# modified model should run just like the regular model but with additional hyperparameters and extra data in results
results = model.transcribe('audio.mp3')
stab_segments = results['segments']
first_segment_word_timestamps = stab_segments[0]['whole_word_timestamps']
print("-----------------------------------------------")

# print word,timestamp,confidence scrores for entire transcription
for stab_segment in stab_segments:
    segment_word_timestamp = stab_segment['whole_word_timestamps']
    for word in segment_word_timestamp:
        print(word)

# or to get token timestamps that adhere more to the top prediction
from stable_whisper import stabilize_timestamps
stab_segments = stabilize_timestamps(results, top_focus=True)
print("-----------------------------------------------")
print(stab_segments)



# word-level
from stable_whisper import results_to_word_srt
# after you get results from modified model
# this treats a word timestamp as end time of the word
# and combines words if their timestamps overlap
print("-----------------------------------------------")
results_to_word_srt(results, 'audio.srt')  #combine_compound=True if compound words are separate
print("-----------------------------------------------")