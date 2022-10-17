import spacy
import nltk
import string
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
from collections import OrderedDict
from nltk.corpus import wordnet
from spacy import displacy
from collections import Counter
import preProcess
import qaProcess
import demoTriple

paragraph_examples = 'Ege University is a public research university in İzmir, Turkey. It was founded in 1955. It is the first university to start courses in İzmir and the fourth oldest university in Turkey. Ege University in Bornova, a district of Izmir, the third largest city in Turkey.'
answer_examples = ['1955', 'No Answer']
question_examples = ['When was Ege University founded?','What is the second oldest university in Turkey?']

paragraph = paragraph_examples

#Question that has an answer
question = question_examples[0]
answer = answer_examples[0]

question = preProcess.punctionProcess(question)
X_list = word_tokenize(question)        
questionSearch = qaProcess.defineQuestionTerm([X_list])  
textSearch, path = qaProcess.searchWord(questionSearch, paragraph, False)
texts = path.split('\n')

sel_sentence = ''
for txt in texts:
    if (str(txt).find(answer.lower()) != -1 or str(txt).find(answer) != -1):
        sentence = str(txt).split('sentence - ')
        sentence = str(sentence[1]).strip()
        sel_sentence = str(sentence).replace('\n', '').strip()
        break

print("Candidate sentence: " + sel_sentence)
svoList, corefParag, corefSent, sub_rel_obj, processes = demoTriple.demo(question_examples[0], paragraph, answer, sel_sentence, False, True)
print("Candidate sentence (coreference resolution): " + str(corefSent))
print("Related triples: " + str(sub_rel_obj))
svo = ''
ind = 1
for trp in svoList:
    trp = str(trp).replace('\'subject\'', 'subject')
    trp = str(trp).replace('\'relation\'', 'relation')
    trp = str(trp).replace('\'object\'', 'object')
    svo += str(ind) + '- ' + trp[1:-1] + '\n'
    ind += 1
print(processes)

#Question that has no answer
question = question_examples[1]
answer = answer_examples[1]

svoList, corefParag, corefSent, sub_rel_obj, processes = demoTriple.demo(question_examples[1], paragraph, '', '', True, False)
svo = ''
ind = 1
for trp in svoList:
    trp = str(trp).replace('\'subject\'', 'subject')
    trp = str(trp).replace('\'relation\'', 'relation')
    trp = str(trp).replace('\'object\'', 'object')
    svo += str(ind) + '- ' + trp[1:-1] + '\n'
    ind += 1
print(processes) 