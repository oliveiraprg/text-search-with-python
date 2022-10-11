from bs4 import BeautifulSoup
import urllib3
from urllib.parse import urljoin


def crawl(pagina):
    http = urllib3.PoolManager()
    
    try:
        dados_pagina = http.request('GET', pagina)
    except:
        print('Erro ao abrir a pagina ' + pagina)
        
    sopa = BeautifulSoup(dados_pagina.data, 'lxml')
    links = sopa.find_all('a')
    for link in links:

        if 'href' in link.attrs:
            url = urljoin(pagina, str(link.get('href')))
            #if url != link.get('href'):
            if url.find("'") != -1:
                continue
            print(url)
            url = url.split('#')[0]
            print(url)
            
                
crawl('https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o')