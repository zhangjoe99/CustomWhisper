from lhotse import CutSet, RecordingSet, align_with_torchaudio, annotate_with_whisper, MonoCut
from pydub import AudioSegment
from tqdm import tqdm


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


sound = AudioSegment.from_mp3("audio.mp3")
sound = sound.set_channels(1)
sound.export("audio.wav", format="wav")

recordings = RecordingSet.from_dir("./", pattern="audio.wav")

cuts = list(annotate_with_whisper(recordings))
cuts_aligned = align_with_torchaudio(cuts)

results = []
for cut in tqdm(cuts_aligned, desc="Progress"):
    # convert to list of dictionaries {word,confidence,start,end}
    results.extend(convert_cut(cut))

for result in results:
    print(result)