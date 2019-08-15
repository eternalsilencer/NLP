import jieba
import jieba.analyse
import codecs
import os


def stop_words(file_path):
    stop_words_set = set()
    with codecs.open(file_path, encoding="utf8") as f:
        for word in f.readlines():
            stop_words_set.add(word.strip('\n'))
    return stop_words_set


def file_cut(text_name, target, stop_words_set):
    f = codecs.open(text_name, 'r', encoding="utf8")
    line = f.readline()
    while line:
        cut_line = list(jieba.cut(line))
        for word in cut_line:
            if word in stop_words_set:
                cut_line.remove(word)
        line_seg = " ".join(cut_line)
        target.writelines(line_seg)
        line = f.readline()
    f.close()


def run():
    stop_words_file = '.\chinese_stop_words.txt'
    dir_path = '.\process'
    stop_words_set = stop_words(stop_words_file)

    target = codecs.open(".\jieba_cut\wiki_seg.txt", 'w', encoding="utf8")

    for name in os.listdir(dir_path):
        text_name = os.path.join(dir_path, name)
        print(text_name)
        file_cut(text_name, target, stop_words_set)
        print('{0} has been processed !'.format(text_name))
    target.close()


if __name__ == '__main__':
    run()