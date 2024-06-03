import functools
from datetime import timedelta
from pprint import pp, pprint

import srt
from ja_sentence_segmenter.common.pipeline import make_pipeline
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation
from su_audio_utils import AudioWav

split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
concat_tail_no = functools.partial(concatenate_matching, former_matching_rule=r"^(?P<result>.+)(の)$",
                                   remove_former_matched=False)
segmenter = make_pipeline(normalize, split_newline, concat_tail_no, split_punc2)

# Golden Rule: Simple period to end sentence #001 (from https://github.com/diasks2/pragmatic_segmenter/blob/master/spec/pragmatic_segmenter/languages/japanese_spec.rb#L6)
# text = """
# これは日本語のテキストです。これは二つ目の文です！そして、これは三つ目の文ですか？
# 私は「はい。そうです。」と答えた。
# このツールも、textlint内部で用いられているパーサを使って高度な解析をしているため、文の途中で改行されているケースでも精度高く分割できています。
# また、「」等の扱いが私好みなことと、処理性能が結構早いことも魅力です。
# """
# from pprint import pprint
# for sentence in segmenter(text):
# print(sentence)
# pprint(list(segmenter(text)))
import budoux

budoux_parser = budoux.load_default_japanese_parser()


# 1. 分句
def split_paragraph(text: str) -> list[str]:
    return list(segmenter(text))


SUBTITLE_ONE_LINE_LIMIT = 25


def combine_elements_until_max_length(text, max_length):
    data = budoux_parser.parse(text)
    pprint(data)
    if not data:
        return []
    combined_list = []
    current_string = ""

    for item in data:
        if len(current_string + item) <= max_length:
            current_string += item
        else:
            combined_list.append(current_string)
            current_string = item

    # 最後のcurrent_stringをリストに追加
    if current_string:
        combined_list.append(current_string)

    return combined_list


def gen_subtitle(sentences: list):
    res: list[list[str]] = []
    curr_str = ""
    for sentence in sentences:
        # 单行就过大了
        if len(sentence) > SUBTITLE_ONE_LINE_LIMIT:
            sub_sentences = combine_elements_until_max_length(sentence, SUBTITLE_ONE_LINE_LIMIT)
            # res.extend(sub_sentences)
            res.append(sub_sentences)
        else:
            res.append([sentence])
            # if curr_str:
            #     if len(curr_str + sentence) > SUBTITLE_ONE_LINE_LIMIT:
            #         res.append([curr_str])
            #         curr_str = sentence
            #     else:
            #         curr_str += sentence

    # if curr_str:
    #     res.append(curr_str)
    return res


def align_subtitle(sentences: list[str], subtitleGroup: list[list[str]], audios: list[AudioWav]) -> list[srt.Subtitle]:
    """
    @param sentences: 分句
    @param subtitleGroup: 每一个分句都有一个或多个字幕
    """
    # res = []
    subtitles: list[srt.Subtitle] = []
    last_subtitle = 0
    for i, subtitle in enumerate(subtitleGroup):
        audioWav = audios[i]
        # if len(subtitle) > 1:
        # 生成多个字幕
        duration = audioWav.get_duration()
        duration += 0.5
        for sub in subtitle:
            sub_duration_rate = len(sub) / len(sentences[i]) * 1.0
            sub_duration = duration * sub_duration_rate
            subtitles.append(
                srt.Subtitle(
                    index=i + 1,
                    start=timedelta(seconds=last_subtitle),
                    end=timedelta(seconds=last_subtitle + sub_duration),
                    content=sub,
                )
            )
            last_subtitle += sub_duration

            # res.append((sub, audioWav))

        # res.append((subtitle, audioWav))
    return subtitles
