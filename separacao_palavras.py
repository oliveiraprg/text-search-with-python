import re
import nltk


nltk.download()
stop_words = nltk.corpus.stopwords.words('portuguese')
stop_words.append('é')
spliter = re.compile('\\W+')
lista_palavras = []
lista = [palavra for palavra in spliter.split('Linguagem de programação é massa – Wikipédia, a enciclopédia livre') if palavra != '']
for palavra in lista:
    if palavra.lower() not in stop_words:
        if len(palavra) > 1:
            lista_palavras.append(palavra.lower())