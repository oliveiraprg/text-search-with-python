import urllib3

http = urllib3.PoolManager()
pagina = http.request('GET', 'https://iaexpert.academy/')
pagina.status
pagina.data
