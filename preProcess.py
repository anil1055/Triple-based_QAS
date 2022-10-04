import nltk
import string
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize

def punctionProcess(text):
    out = str(text).maketrans('','', string.punctuation)
    result = str(text).translate(out)
    
    return result

#punktTokenizer for sentence detection
def punktSentenceTokenizer(paragraph):
    sent_tokenizer = nltk.tokenize.PunktSentenceTokenizer()
    sentences = sent_tokenizer.tokenize(paragraph)
    updateSentence = solveSentenceTokenizer(sentences)
    if len(updateSentence) == 0:
        updateSentence = sentences

    return updateSentence

#POS Tagging
def posTag(text):
    txt = word_tokenize(text)
    pos = nltk.pos_tag(txt)

    return pos

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
# Lemmatize with POS Tag
from nltk.corpus import wordnet
def get_wordnet_pos(word):
    tag = nltk.pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}

    return tag_dict.get(tag, wordnet.NOUN)

lemmatizer=WordNetLemmatizer()
def lemmaProcess(sentence):       
    input_str=word_tokenize(sentence)
    txt = ''
    for word in input_str:
        txt += lemmatizer.lemmatize(word, get_wordnet_pos(word)) + ' ' #, get_wordnet_pos(word)
    sentence = str(txt).strip()

    return sentence

import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm

nlp = en_core_web_sm.load()
#NER process for preprocessing
def NerRecognition(article, answ_list):
    article = nlp(article)
    
    #labels = [x.label_ for x in article.ents]
    #Counter(labels)
    #sentences = [x for x in article.sents]
    #print(dict([(str(x), x.label_) for x in nlp(str(sentences[0])).ents]))

    #Removed number delete process: number = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"] ner_list = [] delete = [] for ner in ner_: ner_list.append(ner) for sayi in number: if str(ner).find(sayi) != -1: delete.append(ner) break for sil in delete: ner_list.remove(sil)
    items = [x.text for x in article.ents]   
    ner_list = Counter(items).keys()
    sw = stopwords.words('english') 
    for ner in ner_list:
        if str(ner).find('\'s') != -1:
            indx = str(ner).index('\'s')
            ner = ner[:indx]
        if str(ner).find(' ') != -1:                  
            ner_ = str(ner).split(' ')
            islow = False
            if str(ner_[len(ner_)-1]).islower() == True:
                islow = True
            try:
                ind = sw.index(ner_[0])
            except:
                uri = ""
                for i in ner_:
                    if islow == False:
                        try:
                            try:
                                ner_list.index(i)
                            except:
                                ind = answ_list.index(i)
                                answ_list.remove(str(i).strip())
                            uri += str(i)  + "_" 
                        except:
                            uri += str(i) + "_"                            
                if uri != "": answ_list.append(str(uri[:-1]))
        else:
            for ans in answ_list:
                if ans.find(ner) != -1:
                    answ_list.remove(ans)
                    answ_list.append(ner)
                    break
    return answ_list


#developed solve for sentence tokenizer error
def solveSentenceTokenizer(sentences):
    firstStage = []
    ind = 0
    indList = []
    last = []
    #If next sentence first word's first letter is lower or numeric char, combine with sentences
    s = ''
    for sentence in sentences:
        if ind+1 < len(sentences):
            words = word_tokenize(sentences[ind+1])
            word = words[0]
            if str(word).islower() == True or str(word).isnumeric() == True:
                firstStage.append(sentence+ ' ' + sentences[ind+1])
                s += sentence+ ' ' + sentences[ind+1]
                last.append(ind+1)
                if ind+1 - last[len(last)-2] == 1:
                    sent = firstStage[len(firstStage)-2]
                    firstStage.remove(firstStage[len(firstStage)-2])
                    firstStage.remove(firstStage[len(firstStage)-1])
                    sent += ' ' + sentences[ind+1]
                    firstStage.append(sent)
                    s += sent
            else:
                firstStage.append(sentence)  
        else:
                firstStage.append(sentence) 
        ind += 1
    for ind in range(0, len(firstStage)-1):
        if str(firstStage[ind]).find(firstStage[ind+1]) != -1:
            indList.append(ind+1)
    indList.sort(reverse=True)
    for ind in indList:
        firstStage.remove(firstStage[ind])
    #If sentence containing max 2 word, combines with next sentences
    secondStage = []
    ind = 0
    for sentence in firstStage:
        words = word_tokenize(sentence) 
        if len(words) < 3:
            if  ind+1 < len(firstStage):
                secondStage.append(sentence + ' ' + firstStage[ind+1])
        else:
            if len(secondStage) > 0:
                if str(secondStage[len(secondStage)-1]).find(sentence) == -1:
                    secondStage.append(sentence)
            else:
                secondStage.append(sentence)
        ind += 1
    #Previous word is uppercase, but last word's first character is uppercase with max 3 length => combine with next sentences 
    lastSentences = []
    ind = 0
    for update in secondStage:
        words = word_tokenize(update) 
        if len(words) >= 2:
            word = words[len(words)-2]
            if len(lastSentences) != 0:
                if str(lastSentences[len(lastSentences)-1]).find(update) != -1:
                    ind += 1
                    continue
            if str(word[0]).isupper() == True and len(word) < 4 and len(words) >= 3:
                word = words[len(words)-3]
                if str(word[0]).islower() == True and len(secondStage) > ind+1:
                    lastSentences.append(update + ' ' + secondStage[ind+1])
                else:
                    lastSentences.append(update)
            else:
                lastSentences.append(update)
        ind += 1
    return lastSentences