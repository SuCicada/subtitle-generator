import base64
import requests
import su_audio_utils
from su_audio_utils import AudioWav


def get_sentences_audio(sentences) -> list[AudioWav]:
    res = []
    for sentence in sentences:
        audioWav = get_audio(sentence)
        if audioWav:
            empty_audio = su_audio_utils.generate_silent_wav(0.5, audioWav.sampling_rate)
            merged_audio = su_audio_utils.merge_wav_files([empty_audio, audioWav])
            res.append(merged_audio)
        else:
            print("Failed to get audio for sentence: ", sentence)
    return res


def get_audio(text):
    url = "https://api.sucicada.top/tts-hub/ttsapi/generate_audio"
    data = {"text": text,
            "tts_engine": "lain_style_bert_vits2",
            "language": "ja",
            }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        print("POST request successful!")
        response_data = response.json()
        sampling_rate = response_data["sampling_rate"]
        audio = response_data["audio"]
        wav_bytes = base64.b64decode(audio)
        audioWav = su_audio_utils.AudioWav(sampling_rate=sampling_rate, wav_bytes=wav_bytes)
        return audioWav

    else:
        print("POST request failed.", response.status_code, response.text)
        return None
