import json
import time
from threading import Thread
from watson_developer_cloud import ToneAnalyzerV3
import queue
import datetime
def stats(qPath,aPath):
    with open(qPath, encoding='utf-8') as q,\
         open(aPath, encoding='utf-8') as a:
        qNoemo,aNoemo,qEmo,aEmo,same,notsame = 0,0,0,0,0,0
        for qtext, atext in zip(q, a):
            qO = qtext.split("+++$+++")
            aO = atext.split("+++$+++")
            if qO[2] == "#noemo\n":
                qNoemo += 1
            else:
                qEmo += 1
            if aO[2] == "#noemo\n":
                aNoemo += 1
            else:
                aEmo += 1
            if qO[2] == aO[2]:
                same += 1
            else:
                notsame += 1
    print("qEmo: ",qEmo)
    print("qNoemo: ",qNoemo)
    print("aEmo: ",aEmo)
    print("aNoemo: ", aNoemo)
    print("q == a: " , same)
    print("else: " ,notsame)
def emo(emo):
    return {
        '#noemo\n': "#noEmo",
        '#anger\n': "#Emo",
        '#disgust\n': "#Emo",
        '#fear\n': "#Emo",
        '#happiness\n': "#Emo",
        '#sadness\n': "#Emo",
        '#suprise\n': "#Emo",
    }.get(emo, "#error")
def addidforinfer(filetoedit,output_file):
    with open(filetoedit, encoding='utf-8') as q:
        i = 1
        qfile = open(output_file, 'w+', encoding="UTF-8")
        qlist = list()
        for qtext in q:
            qlist.append(str(i)+"+++$+++"+qtext)
            i += 1
        qfile.writelines(qlist)
        qfile.close()
def score2binEmo(score_file,output_file):
    binemolist = list()
    with open(score_file,encoding='utf-8') as f:
        qfile = open(output_file, 'w+', encoding="UTF-8")
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
            binemolist.append(x[0]+"+++$+++"+emo+"\n")
        qfile.writelines(binemolist)
        qfile.close()
def precisionrecall(filename,gold_file,pred_file):
    TP,TN,FP,FN = 0,0,0,0
    with open(gold_file, encoding='utf-8') as g, \
         open(pred_file, encoding='utf-8') as p:
        for gold,pred in zip(g,p):
            if gold.split("+++$+++")[1] == "#Emo\n" and pred.split("+++$+++")[1] == "#Emo\n":
                TP +=1
            if gold.split("+++$+++")[1] == "#noEmo\n" and pred.split("+++$+++")[1] == "#Emo\n":
                FP+=1
            if gold.split("+++$+++")[1] == "#noEmo\n" and pred.split("+++$+++")[1] == "#noEmo\n":
                TN+=1
            if gold.split("+++$+++")[1] == "#Emo\n" and pred.split("+++$+++")[1] == "#noEmo\n":
                FN+=1
        print("TP FP TN FN")
        print(TP,FP,TN,FN)
        print("precision")
        print(TP/(TP+FP))
        print("recall")
        print(TP / (TP + FN))
        print("accutacy")
        print((TP+TN)/(TP+FP+TN+FN))
        print("")
def sortscore(filetoedit):
    dic = dict()
    with open(filetoedit, encoding='utf-8') as q:
        for item in q:
            dic[item.split("+++$+++")[0]] = item.split("+++$+++")[1]
    file = open(filetoedit+"_sorted",mode="w+" ,encoding='utf-8')
    for i in range(1,len(dic)+1):
        file.writelines(str(i)+"+++$+++"+dic[str(i)])
    file.close()
# The following parts is for calling IBM WATSON
def idinfer2list(file_path):
    li = list()
    with open(file_path, encoding='UTF-8') as f:
        for l in f:
            x = l.split("+++$+++")
            li.append((x[0].strip(), x[1]))
        return li
def stripTextforScore(s: str):
    news = s.replace(".  ",".")
    news = news.replace(". ", ".")
    news = news.replace("?  ", "?")
    news = news.replace("?  ","?")
    news = news.replace("!  ", "!")
    news = news.replace("!  ", "!")
    news = news.replace("\n","  \n")
    return news
def callapi(q,result,i):
    tone_analyzer = ToneAnalyzerV3(
        username='YOURS',
        password='YOURS',
        version='2017-09-26')
    while not q.empty():
        work = q.get()
        try:
            tone = tone_analyzer.tone(tone_input=stripTextforScore(work[1]), content_type='text/plain')
        except:
            time.sleep(10)
            tone = tone_analyzer.tone(tone_input=stripTextforScore(work[1]), content_type='text/plain')
        result.append(work[0] + "+++$+++" + json.dumps(tone) + "\n")
        if len(result)%100 == 0:
            print(str(len(result)) , str(datetime.datetime.now().time()))
            print(work[0] + "+++$+++" + json.dumps(tone) + "\n")
        q.task_done()
    return True
def classemo(filetoscore):
    q = queue.Queue(maxsize=0)
    li = idinfer2list("./result/"+filetoscore+"_id")
    result = list()
    num = 0
    for line in li:
        q.put(line)
    for i in range(10):
        print('Starting thread ', i)
        worker = Thread(target=callapi, args=(q, result,num))
        worker.setDaemon(True)  # setting threads as "daemon" allows main program to
        # exit eventually even if these dont finish
        # correctly.
        worker.start()
    q.join()
    print('All tasks completed.')
    print("saving")
    file = open("./result/score_of_"+filetoscore, 'w+', encoding="UTF-8")
    file.writelines(result)
    file.close()
    print("saved")

if __name__ == "__main__":
    filetoscore = "YOUR_FILE"
    addidforinfer("./result/"+filetoscore,"./result/"+filetoscore+"_id")
    classemo(filetoscore)
    score2binEmo('./result/score_of_'+filetoscore,'./result/'+filetoscore+'_binEmo')
    sortscore('./result/'+filetoscore+'_binEmo')
    precisionrecall(filetoscore,"./result/a_binEmo_score", "./result/"+filetoscore+"_binEmo_sorted")
