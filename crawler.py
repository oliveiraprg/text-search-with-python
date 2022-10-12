from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
import re
import nltk
import pymysql
from secret_settings import password_db


def insere_palavra_localizacao(idurl, idpalavra, localizacao):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root', passwd=password_db, db='indice', autocommit=True) 
    cursor = conexao.cursor()
    cursor.execute('insert into palavra_localizacao (idurl, idpalavra, localizacao) values (%s, %s, %s)', (idurl, idpalavra, localizacao))
    idpalavra_localizacao = cursor.lastrowid
    cursor.close()
    conexao.close()
    
    return idpalavra_localizacao


def insere_palavra(palavra):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root', passwd=password_db, db='indice', autocommit=True) 
    cursor = conexao.cursor()
    cursor.execute('insert into palavras (palavra) values (%s)', palavra)
    idpalavra = cursor.lastrowid
    cursor.close()
    conexao.close()
    
    return idpalavra


def palavra_indexada(palavra):
    retorno = -1 #não existe a palavra no indice
    global password_db
    conexao = pymysql.connect(host='localhost', user='root', passwd=password_db, db='indice', autocommit=True) 
    cursor = conexao.cursor()
    cursor.execute('select idpalavra from idpalavras where palavra %s', palavra)
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    
    return retorno


def insere_pagina(url):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root', passwd=password_db, db='indice', autocommit=True) 
    cursor = conexao.cursor()
    cursor.execute('insert into urls (url) values (%s)', url)
    idpagina = cursor.lastrowid
    cursor.close()
    conexao.close()
    
    return idpagina
    
    
def pagina_indexada(url):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root', passwd=password_db, db='indice')   
    retorno = -1 #não existe a pagina
    cursor_url = conexao.cursor()
    cursor_url.execute('select idurl from urls where url = %s', url)
    if cursor_url.rowcount > 0:
        idurl = cursor_url.fetchone()[0]
        cursor_palavra = conexao.cursor()
        cursor_palavra.execute('select idurl from palavra_localizacao where idurl = %s', idurl)
        if cursor_palavra.rowcount > 0:
            retorno = -2 # Existe pagina com palavras cadastradas
        else:
            retorno = idurl # existe a pagina sem palavras
        cursor_palavra.close()
    
    cursor_url.close()
    conexao.close()
    
    return retorno


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
