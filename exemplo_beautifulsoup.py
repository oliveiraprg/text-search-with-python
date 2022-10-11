from bs4 import BeautifulSoup
import urllib3

http = urllib3.PoolManager()
pagina = http.request('GET', 'https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o')
pagina.status
sopa = BeautifulSoup(pagina.data, 'lxml')
sopa.title
links = sopa.find_all('a')
for link in links:
    print(link.get('href'))
    print(link.contents)