from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin
import re
import nltk
import pymysql
from secret_settings import password_db


def insere_palavra_localizacao(idurl, idpalavra, localizacao):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice', autocommit=True) 
    cursor = conexao.cursor()
    cursor.execute('INSERT INTO palavra_localizacao (idurl, idpalavra, localizacao) VALUES (%s, %s, %s)', (idurl, idpalavra, localizacao))
    idpalavra_localizacao = cursor.lastrowid
    cursor.close()
    conexao.close()
    
    return idpalavra_localizacao


def insere_palavra(palavra):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice', autocommit=True,
                              use_unicode=True, charset='utf8mb4') 
    cursor = conexao.cursor()
    cursor.execute('INSERT INTO palavras (palavra) VALUES (%s)', palavra)
    idpalavra = cursor.lastrowid
    cursor.close()
    conexao.close()
    
    return idpalavra


def palavra_indexada(palavra):
    retorno = -1 # Não existe a palavra no indice
    global password_db
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice', autocommit=True,
                              use_unicode=True, charset='utf8mb4') 
    cursor = conexao.cursor()
    cursor.execute('SELECT idpalavra FROM palavras WHERE palavra = %s', palavra)
    if cursor.rowcount > 0:
        retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    
    return retorno


def insere_pagina(url):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice', autocommit=True) 
    cursor = conexao.cursor()
    cursor.execute('INSERT INTO urls (url) VALUES (%s)', url)
    id_pagina = cursor.lastrowid
    cursor.close()
    conexao.close()
    
    return id_pagina
    
    
def pagina_indexada(url):
    global password_db
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice')   
    retorno = -1 # Não existe a pagina
    cursor_url = conexao.cursor()
    cursor_url.execute('SELECT idurl FROM urls WHERE url = %s', url)
    if cursor_url.rowcount > 0:
        idurl = cursor_url.fetchone()[0]
        cursor_palavra = conexao.cursor()
        cursor_palavra.execute("SELECT idurl FROM palavra_localizacao WHERE idurl = %s", (idurl))
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


def indexador(url, sopa):
    indexada = pagina_indexada(url)
    if indexada == -2:
        print('Url já cadastrada')
        return 
    elif indexada == -1:
        id_nova_pagina = insere_pagina(url)
    elif indexada > 0:
        id_nova_pagina = indexada
        
    texto = get_texto(sopa)
    palavras = separa_palavras(texto)
    for i in range(len(palavras)):
        palavra = palavras[i]
        id_palavra = palavra_indexada(palavra)
        if id_palavra == -1:
            id_palavra = insere_palavra(palavra)
        insere_palavra_localizacao(id_nova_pagina, id_palavra, i)


def crawl(paginas, profundidade):
    i=0
    while i < profundidade:
        novas_paginas = set()
        try:
            for pagina in paginas:
                print(len(pagina))
                http = urllib3.PoolManager()
                try:
                    if len(pagina) > 255:
                        continue
                    dados_pagina = http.request('GET', pagina)
                except:
                    print('Erro ao abrir a pagina ' + pagina)
                    continue
                    
                sopa = BeautifulSoup(dados_pagina.data, 'lxml')
                indexador(pagina, sopa)
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
        except:
            print('Erro ao abrir a pagina ' + pagina)
            continue
        paginas = novas_paginas    
        i += 1
    print('Todas paginas percorridas')
        
        
            
lista_paginas = ['https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o']

crawl(lista_paginas, 2)
