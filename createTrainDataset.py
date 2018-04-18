import nltk
import json
import ast
import os
import purge
nltk.download('averaged_perceptron_tagger')

def tagpos(s):
    text = nltk.word_tokenize(s)
    pos = nltk.pos_tag(text)
    for tup in pos:
        if tup[1] == "RB":
            if tup[0] == "n't":
                continue
            s = s.replace(tup[0]+" ","<adv> "+tup[0]+" </adv> ")
        if tup[1] == "JJ":
            s = s.replace(tup[0]+" ","<adj> "+tup[0]+" </adj> ")
        # This will create duplicate tag
    for i in range(6):
        s = s.replace("<adv> <adv>","<adv>")
        s = s.replace("</adv> </adv>", "</adv>")
        s = s.replace("<adj> <adv>", "<adj>")
        s = s.replace("</adj> </adj>", "</adv>")
    return s
class EmoTagger:
    def __init__(self):
        self.emolist = {}
        with open("NRC-Emotion-Lexicon-Wordlevel-v0.92.txt", "r", encoding="utf-8") as nrc_file:
            for line in nrc_file.readlines():
                splited = line.replace("\n", "").split("\t")
                word, emotion, value = splited[0], splited[1], splited[2]
                if word in self.emolist.keys():
                    self.emolist[word].append((emotion, int(value)))
                else:
                    self.emolist[word] = [(emotion, int(value))]
    def tagEmo(self,s):
        # Tag word if emotion present
        text = nltk.word_tokenize(s)
        for word in text:
            emo = self.emolist.get(word,"")
            for tup in emo:
                if tup[0] is "positive" or tup[0] is "negative":
                    continue
                if tup[1] == 1:
                    s = s.replace(word, "<emo> " + word+ " </emo>")
                    break
        for i in range(10):
            s = s.replace("<emo> <emo>","<emo>")
            s = s.replace("</emo> </emo>", "</emo>")
        return s
def _createEmoDict():
    dic = dict()
    with open("movielinescore",encoding='utf-8') as f:
        for l in f:
            x = l.split("+++$+++")
            j = json.loads(x[1])

            if j['document_tone']['tones'] == []:
                emo = "#noEmo"
            else:
                for tones in j['document_tone']['tones']:
                    if tones["tone_id"] == "joy" or \
                                    tones["tone_id"] == "sadness" or\
                                    tones["tone_id"] == "fear" or \
                                    tones["tone_id"] == "anger":
                        emo = "#Emo"
                        break
                    else:
                        emo = "#noEmo"
            dic[x[0].strip()] = emo
        return dic
def _createMovieLineDict():
    dic = dict()
    with open("movie_lines.txt",encoding='Windows-1252') as f:
        for l in f:
            x = l.split("+++$+++")
            dic[x[0].strip()] = x[4]
        return dic

def _savefile(dirname,qlist,alist):
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    qfile = open('./'+dirname+'/train.q', 'w+', encoding="UTF-8")
    afile = open('./'+dirname+'/train.a', 'w+', encoding="UTF-8")
    qfile.writelines(qlist)
    qfile.close()
    afile.writelines(alist)
    afile.close()
    qlist.clear()
    alist.clear()

def _createCovlist():
    convs = list()
    with open("movie_conversations.txt", encoding='Windows-1252') as f:
        for l in f:
            convs.append(l)
    return convs
if __name__ == "__main__":
    qlist,alist = list(),list()
    emotag = EmoTagger()
    dic = _createMovieLineDict()
    emodic = _createEmoDict()
    movielines = _createCovlist()
    # baseline model
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(purge.purge(dic[conv[i]]))
            alist.append(purge.purge(dic[conv[i+1]]))
    _savefile("baseline", qlist, alist)
    # tag pos
    # to let people know the program is not dead but painfully slow
    poscount = 0
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            poscount += 1
            qlist.append(tagpos(purge.purge(dic[conv[i]])))
            alist.append(tagpos(purge.purge(dic[conv[i+1]])))
            print(poscount)
    _savefile('tagpos',qlist,alist)
    # tag Emolex
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(emotag.tagEmo(purge.purge(dic[conv[i]])))
            alist.append(emotag.tagEmo(purge.purge(dic[conv[i+1]])))
    _savefile('tagemo', qlist, alist)
    # tag q for its sentence emotion
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(purge.purge(dic[conv[i]]).replace("\n"," "+emodic[conv[i]]+"\n"))
            alist.append(purge.purge(dic[conv[i+1]]))
    _savefile('qtaggedq', qlist, alist)
    # tag a for its sentence emotion
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(purge.purge(dic[conv[i]]))
            alist.append(purge.purge(dic[conv[i+1]]).replace("\n", " " + emodic[conv[i+1]] + "\n"))
    _savefile('ataggeda', qlist, alist)

    # tag q and a for its sentence emotion
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(purge.purge(dic[conv[i]]).replace("\n", " " + emodic[conv[i]] + "\n"))
            alist.append(purge.purge(dic[conv[i+1]]).replace("\n", " " + emodic[conv[i+1]] + "\n"))
    _savefile('qaitself', qlist, alist)

    # tag a with q sentence emotion
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(purge.purge(dic[conv[i]]))
            alist.append(purge.purge(dic[conv[i+1]]).replace("\n", " " + emodic[conv[i]] + "\n"))
    _savefile('ataggedq', qlist, alist)

    # tag q with a sentence emotion
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(purge.purge(dic[conv[i]]).replace("\n", " " + emodic[conv[i]] + "\n"))
            alist.append(purge.purge(dic[conv[i + 1]]))
    _savefile('qtaggeda', qlist, alist)

    # tag q with a sentence emotion before context payload
    for l in movielines:
        x = l.split("+++$+++")
        conv = ast.literal_eval(x[3].strip())
        for i in range(0, len(conv) - 1):
            if "<nos>" in dic[conv[i]] or "<nos>" in dic[conv[i+1]]:
                continue
            qlist.append(emodic[conv[i+1]]+" "+purge.purge(dic[conv[i]]))
            alist.append(purge.purge(dic[conv[i + 1]]))
    _savefile('qtaggedaF', qlist, alist)