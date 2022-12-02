from lhotse import RecordingSet, align_with_torchaudio, annotate_with_whisper, MonoCut
from pyannote.audio import Pipeline

import urllib.request
from pydub import AudioSegment
import uuid

# Helper function for whisper reponse
def convert_cut(cut: MonoCut):
    results = []
    for supervision in cut.supervisions:
        words = supervision.text.split()
        for word, alignment_item in zip(words, supervision.alignment['word']):
            results.append({
                "word": word,
                "confidence": alignment_item.score,
                "start": alignment_item.start,
                "end": alignment_item.start + alignment_item.duration
            })
    return results

# Reformat/Edit pyannote response
def reformat_pyannote(diarization):
    prev_start = 0
    prev_end = 0
    prev_speaker = None
    result = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        if prev_speaker == None:
            prev_speaker = speaker
            prev_start = turn.start
            prev_end = turn.end
            continue

        if turn.end - turn.start < 0.5:
            continue

        if turn.start < prev_end:
            result.append((prev_start, turn.start, prev_speaker))
            if turn.end < prev_end:
                result.append((turn.start, turn.end, speaker))
                prev_start = turn.end
            else:
                prev_start = turn.start
                prev_end = turn.end
                prev_speaker = speaker
        else:
            if prev_speaker == speaker:
                prev_end = turn.end
            else:
                result.append((prev_start, prev_end, prev_speaker))
                prev_start = turn.start
                prev_end = turn.end
                prev_speaker = speaker

    result.append((prev_start, prev_end, prev_speaker))
    return result

def transcribe_audio(audio_url):
    # Set up
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization@2.1", use_auth_token="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")
    filebasename = "audio"

    # Download audio file
    urllib.request.urlretrieve(audio_url, filebasename + ".mp3")

    # Convert audio file
    sound = AudioSegment.from_mp3(filebasename + ".mp3")
    sound.export(filebasename + ".wav", format="wav")

    # Call pyannote
    diarization = pipeline(filebasename + ".wav")
    pyannote_result = reformat_pyannote(diarization)

    # Call whisper
    sound = sound.set_channels(1)
    sound.export("audio.wav", format="wav")

    recordings = RecordingSet.from_dir("./", pattern="audio.wav")

    cuts = list(annotate_with_whisper(recordings))
    cuts_aligned = align_with_torchaudio(cuts)

    whisper_result = []
    for cut in cuts_aligned:
        # convert to list of dictionaries {word,confidence,start,end}
        whisper_result.extend(convert_cut(cut))
    
    # Combine pyannote result with whisper
    words = []
    i = 0

    for word in whisper_result:
        starttime = word['start']
        group = {}
        group['text'] = word['word']
        group['start'] = starttime
        group['end'] = word['end']
        group['confidence'] = word['confidence']

        try:
            while starttime > pyannote_result[i][1]:
                i += 1
        except:
            i -= 1
        
        group['speaker']: pyannote_result[i][2]

        words.append(group)

    # Format return
    ret = {}
    ret['id'] = str(uuid.uuid4())
    ret['status'] = 'completed'
    ret['audio_url'] = audio_url
    # ret['text'] = results['text']
    ret['words'] = words

    return ret

AUDIO_URL = "https://stakwork-uploads-dev.s3.amazonaws.com/short_ep_48_kevin_rooke.mp3"
print(transcribe_audio(AUDIO_URL))