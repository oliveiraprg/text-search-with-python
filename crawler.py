from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
import re
import nltk


def separa_palavras(texto):
    stop_words = nltk.corpus.stopwords.words('portuguese')
    spliter = re.compile('\\W+')
    stemmer = nltk.stem.RSLPStemmer()
    lista_palavras = []
    lista = [palavra for palavra in spliter.split(texto) if palavra != '']
    for palavra in lista:
        if palavra.lower() not in stop_words:
            if len(palavra) > 1:
                lista_palavras.append(stemmer.stem(palavra).lower())
    return lista_palavras


def get_texto(sopa):
    for tags in sopa(['script', 'style']):
        tags.decompose
    return ' '.join(sopa.stripped_strings)


def crawl(paginas, profundidade):
    for i in range(profundidade):
        novas_paginas = set()
        for pagina in paginas:
            http = urllib3.PoolManager()
            
            try:
                dados_pagina = http.request('GET', pagina)
            except:
                print('Erro ao abrir a pagina ' + pagina)
                continue
                
            sopa = BeautifulSoup(dados_pagina.data, 'lxml')
            links = sopa.find_all('a')
            for link in links:
        
                if 'href' in link.attrs:
                    url = urljoin(pagina, str(link.get('href')))
                    #if url != link.get('href'):
                    if url.find("'") != -1:
                        continue
                    url = url.split('#')[0]
                    if url[0:4] == 'http':
                        novas_paginas.add(url)
            paginas = novas_paginas    
            
            
lista_paginas = ['https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o']
crawl(lista_paginas, 2)
