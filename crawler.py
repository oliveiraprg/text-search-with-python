from bs4 import BeautifulSoup
import urllib3


def crawl(pagina):
    http = urllib3.PoolManager()
    try:
        dados_pagina = http.request('GET', pagina)
    except:
        print('Erro ao abrir a pagina ' + pagina)
        
    sopa = BeautifulSoup(dados_pagina.data, 'lxml')
    links = sopa.find_all('a')
    for link in links:
        print(str(link.contents) + str(link.get('href')))


crawl('https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o')