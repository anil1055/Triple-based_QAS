def defineQuestionTerm(preProcess):
    questionSearch = ''
    for terms in preProcess:
        for term in terms:
            if str(term).find('_') != -1:
                term = str(term).replace('_',' ')
            questionSearch += term + ','
    questionSearch = questionSearch[:-1]
    return questionSearch
	
	
def findPath(rateList,textList):
    sortList = []
    sortTxt = ''
    for rate in rateList:
        value = max(rateList)
        ind = rateList.index(value)
        sortList.append(ind)
        rateList[ind] = 0
    for sort in sortList:
        sortTxt += textList[sort] + '\n'
    return sortTxt
	
	
def searchWord(text,paragraph,lemma):
    texts = []
    textSearch = ''
    path = ''
    try:
        if str(text).find(',') != -1:
            texts = str(text).split(',')
        else:
            texts.append(text)  
        par = paragraph          
        sentences = punktSentenceTokenizer(par)
        s_ind = 0
        rateList = []
        textList = []
        for sentence in sentences:         
            sent = punctionProcess(str(sentence))
            if lemma == True:
                sent = lemmaProcess(sent)
                sentence = sent
            c = 0
            qaText = [] 
            qTerm = []
            for i in range(0,len(texts)):
                texts[i] = str(texts[i]).strip()
                if str(sent.lower()).find(texts[i].lower()) != -1:
                    c += 1
                    qTerm.append(str(texts[i]))

            if c != 0:
                textSearch += 'Find question:' + str(qTerm) + ', QCount:' + str(c) + '\nQuestion rate:%' + str(c/len(texts)*100) + '\n' + str(s_ind+1) + '. sentence - ' + sentence + '\n\n'
                rateList.append(c/len(texts)*100)
                textList.append('Find question:' + str(qTerm) + ', QCount:' + str(c) + '\nQuestion rate:%' + str(c/len(texts)*100) + '\n' +  str(s_ind+1) + '. sentence - ' + sentence + '\n\n')
            s_ind += 1
        if len(rateList) != 0:
            path += findPath(rateList,textList)
    except Exception as e:
        print('SearchWord:' + str(e) + ', text:' + str(texts))
    return textSearch, path
	