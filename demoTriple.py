import spacy
from spacy.lang.en import English 
from openie import StanfordOpenIE
import neuralcoref
import preProcess

def OpenIEforSentence(sentence, client):
    svoText = []
    for triple in client.annotate(sentence):
        svoText.append(str(triple))
    return svoText

#spacy==2.1.0
#pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz
nlp_model = spacy.load('en_core_web_sm')
neuralcoref.add_to_pipe(nlp_model)
def coreferenceResolution(paragraph, predictor, method):
    try:
        try:
            while paragraph.index('(') != -1:
                lindx = paragraph.index('(')
                rindx = paragraph.index(')', lindx)
                paragraph = paragraph[:lindx].strip() + ' ' + paragraph[rindx+1:].lstrip()
        except:
            paragraph = paragraph       
        sentences = preProcess.punktSentenceTokenizer(paragraph)
        newParagraph = ''
        for sent in sentences:
            newParagraph += str(sent[:-1]) + '.. '
        if method == 1: #HuggingFace                       
            doc = nlp_model(newParagraph)  # get the spaCy Doc (composed of Tokens)
            paragraph = doc._.coref_resolved
        newSentence = paragraph.split('.. ')
        sentences = []
        paragraph = ''
        for sentence in newSentence:    
            paragraph += sentence[:1].capitalize() + sentence[1:] + '. '
            sentences.append(sentence[:1].capitalize() + sentence[1:] + '. ')
        return sentences, paragraph[:-3]
    except Exception as e:
        print('ErrorCorefRes:' + str(e))
        return paragraph, ""


def wordProcess(question):
    from nltk.corpus import stopwords 
    from nltk.tokenize import word_tokenize
    stop_words = stopwords.words('english') 
    word_tokens = word_tokenize(question)
    filtered_ques = [w for w in word_tokens if not w.lower() in stop_words]
    ansType = NERstatement(question)
    question = ''
    for q in filtered_ques:
        question += q + ' '
    question = question[:-1].strip()

    return question, ansType


def demo(ques, parag_examp, actual_ans, sel_sentence, no_answer = False, preprocess = False, not_squad = False, index_title = 0):     
    
    with StanfordOpenIE() as StanfordClient:
        global context_list
        global title
        svoList = []
        corefSent = ''
        corefParag = ''
        sub_rel_obj = ''
        processes = ''
        if no_answer == False:
            paragraph = ''
            paragNo = 0
            titleInd = 0
            sentence = ''
            question = ''
            actual_answer = ''
            if not_squad == False:
				#SQuAD dataset processes, these function is hidden!
                data = ReadInfos(ques, title)
                paragNo, titleInd, sentence, question, actual_answer = data
                key, paragraph = context_list[int(titleInd)][int(paragNo)]
            else:
                paragraph = parag_examp
                actual_answer = actual_ans
                sentence = sel_sentence
                question = ques.lower()
            paragraph = str(paragraph).replace('\n', '')
            totalFindAnswer = 0
            findAns = 0
            
            sentences = preProcess.punktSentenceTokenizer(paragraph)
            sind = -1
            sPosition = 0
            try:
                for sent in sentences:
                    if str(sent).find(str(sentence).strip()) != -1:
                        sPosition = sind + 1
                        sind += 1
                        break
                    sind += 1    
                if sind == -1:
                    print('Cümle bulma hatası')
                else:
                    corefSent, corefParag = coreferenceResolution(paragraph, "", 1)
                    svoList = OpenIEforSentence(corefSent[sPosition], StanfordClient)
                    corefSent = corefSent[sPosition]
            except Exception as e:
                print("Error LocationCoref:" + str(e))

            answerList = []            
            try:
                for triple in svoList:                 
                    triple = str(triple).split(',')
                    subject = str(str(triple[0]).split(':')[1]).strip()[1:-1].lower()            
                    relation = str(' ' + str(str(triple[1]).split(':')[1]).strip()[1:-1] + ' ').lower()
                    object = str(str(triple[2]).split(':')[1]).strip()[1:-2].lower()
                    if preprocess:
                        subject, ansType = wordProcess(subject)
                        relation, ansType = wordProcess(relation)
                        object, ansType = wordProcess(object)
                    answer = ''
                    if str(question).find(subject) != -1 and str(question).find(relation) != -1:
                        if str(question).find(object) == -1:
                            answer = object
                            sub_rel_obj = triple
                    if str(question).find(object) != -1 and str(question).find(relation) != -1:
                        if str(question).find(subject) == -1:    
                            answer = subject
                            sub_rel_obj = triple
                    if str(question).find(object) != -1 and str(question).find(subject) != -1:
                        if str(question).find(relation) == -1:    
                            answer = relation
                            sub_rel_obj = triple
                    if answer == actual_answer:
                        totalFindAnswer += 1
                    if answer != '':
                        answerList.append(answer)       
            except Exception as e:
                print("Error searchSvo:" + str(e))

            if len(answerList) == 1 and findAns != totalFindAnswer:
                print("Triple found successfully!")  

        else: 
            paragraph = ''
            question = ques.lower()
            if not_squad == False:
				#SQuAD dataset processes, these function is hidden!
                qList, aList = qaProcess.createQuestionAnswer('dev_set', index_title) 
                for q_key, q_value in qList:
                    if q_value.lower() == ques.lower():
                        p_ind = int(str(q_key).split('_')[0])
                key, paragraph = context_list[index_title][p_ind]                 
            else:
                paragraph = parag_examp                
            paragraph = str(paragraph).replace('\n', '')
            triples = []
            corefSent, corefParag = coreferenceResolution(paragraph, "", 1)
            for sent in corefSent:
                svoList = OpenIEforSentence(sent, StanfordClient)
                for svo in svoList:
                    triples.append(svo)
            corefSent = ''
            svoList = triples
            question, answerType = wordProcess(question)
            processes += 'NER answer label: ' + answerType + '\n'
            answer_cont = False
            labels = []
            try:
                for triple in triples: 
                    triple = str(triple).split(',')
                    subject = str(str(triple[0]).split(':')[1]).strip()[1:-1]
                    relation = str(' ' + str(str(triple[1]).split(':')[1]).strip()[1:-1] + ' ')
                    object = str(str(triple[2]).split(':')[1]).strip()[1:-2]
                    if preprocess:
                        subject, ansType = wordProcess(subject)
                        relation, ansType = wordProcess(relation)
                        object, ansType = wordProcess(object)
                    if str(question).find(subject.lower()) != -1 and str(question).find(relation.lower()) != -1:
                        if answerType != '':
                            answer_cont, labels = NERdetection(object.strip(), answerType)
                            processes += str(labels) + '\n'
                        else: answer_cont = True
                    if str(question).find(object.lower()) != -1 and str(question).find(relation.lower()) != -1:   
                        if answerType != '':
                            answer_cont, labels = NERdetection(subject.strip(), answerType)
                            processes += str(labels) + '\n'
                        else: answer_cont = True
                    if str(question).find(object.lower()) != -1 and str(question).find(subject.lower()) != -1: 
                        if answerType != '':
                            answer_cont, labels = NERdetection(relation.strip(), answerType)
                            processes += str(labels) + '\n'
                        else: answer_cont = True
                    if answer_cont == True:
                        break
                if answer_cont == False:                    
                    print("Triple not found successfully!")  
      
            except Exception as e:
                print("Error searchSvo:" + str(e))


        StanfordClient.client.stop()
        return svoList, corefParag, corefSent, sub_rel_obj, processes


def NERdetection(sentence, ansType):
    sentence = nlp_model(sentence)
    labels = [x.label_ for x in sentence.ents]
    answer_cont = False
    if len(labels) != 0:
        for i in range(0, len(labels)):
            if ansType.find(labels[i]) != -1:
                answer_cont = True
                break
    return answer_cont, labels
	
def NERstatement(ques):
    ansType = ''
    if ques.find('who') != -1:
        ansType = 'PERSON'
    if ques.find('when') != -1:
        ansType = 'DATE'
    if ques.find('how many') != -1:
        ansType = 'QUANTITY'
    if ques.find('how much') != -1:
        ansType = 'QUANTITY, MONEY'
    if ques.find('where') != -1:
        ansType = 'GPE'
    pos = app.preProcess.posTag(ques)
    if len(pos)> 2:
        for i in range(len(pos)-1):
            if pos[i][0] == 'what' or pos[i][0] == 'which' or pos[i][0] == 'where' or pos[i][0] == 'whose':
                if pos[i+1][0] == 'people' or pos[i+1][0] == 'person':
                    ansType = 'PERSON'
                if pos[i+1][0] == 'nationality' or pos[i+1][0] == 'religion' or pos[i+1][0] == 'politic':
                    ansType = 'NORP'
                if pos[i+1][0] == 'country' or pos[i+1][0] == 'city' or pos[i+1][0] == 'state':
                    ansType = 'GPE'
                if pos[i+1][0] == 'company' or pos[i+1][0] == 'agency' or pos[i+1][0] == 'institution':
                    ansType = 'ORG'
                if pos[i+1][0] == 'building' or pos[i+1][0] == 'airport' or pos[i+1][0] == 'highway' or pos[i+1][0] == ' bridge':
                    ansType = 'FAC'
                if pos[i+1][0] == 'location' or pos[i+1][0] == 'range':
                    ansType = 'LOC'
                if pos[i+1][0] == 'hurricane' or pos[i+1][0] == 'battle' or pos[i+1][0] == 'war':
                    ansType = 'EVENT'
                if pos[i+1][0] == 'song' or pos[i+1][0] == 'title':
                    ansType = 'WORK_OF_ART'
                if pos[i+1][0] == 'language':
                    ansType = 'LANGUAGE'
                if pos[i+1][0] == 'time' or pos[i+1][0] == 'date' or pos[i+1][0] == 'period' or pos[i+1][0] == 'duration' or pos[i+1][0] == 'year' or pos[i+1][0] == 'month' or pos[i+1][0] == 'day':
                    ansType = 'DATE'
                if pos[i+1][0] == 'percentage':
                    ansType = 'PERCENT'
                if pos[i+1][0] == 'measurement' or pos[i+1][0] == 'weight' or pos[i+1][0] == 'distance':
                    ansType = 'QUANTITY'
    return ansType