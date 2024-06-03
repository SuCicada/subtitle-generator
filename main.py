from datetime import timedelta
import json
from pprint import pprint

import su_audio_utils
from more_itertools import last

from get_tts import get_sentences_audio
from subtitle import gen_subtitle, split_paragraph, align_subtitle
from su_audio_utils import AudioWav, merge_wav_files
import srt

file = "bible_pray_2024-05-29.json"

with open(file, "r") as f:
    json_data = json.load(f)

biblePray = json_data["bible"]["biblePray"]

# print(biblePray)
text = biblePray
# 1. 分句
sentences = split_paragraph(text)
# 2. tts
audios = get_sentences_audio(sentences)
# 3. 生成字幕
subtitleGroup = gen_subtitle(sentences)
# 4. 字幕对齐时间
subtitles = align_subtitle(sentences, subtitleGroup, audios)


# 5. save subtitle and audio
def save():
    srt_data = srt.compose(subtitles)
    with open("example.srt", "w") as f:
        f.write(srt_data)
    # empty_audio = su_audio_utils.generate_silent_wav(0.5, audios[0].sampling_rate)
    # add_space_audios = [elem
    #                     for pair in [zz for zz in zip(audios, [empty_audio] * len(audios))]
    #                     for elem in pair]

    audio = merge_wav_files(audios)
    with open("example.wav", "wb") as f:
        f.write(audio.wav_bytes)


save()

pprint(sentences)
pprint(subtitles)

for subtitle in subtitles:
    print(subtitle)
