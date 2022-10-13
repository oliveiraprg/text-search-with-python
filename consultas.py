import nltk
import pymysql
from secret_settings import password_db


def get_id_palavra(palavra):
    retorno = -1
    stemmer = nltk.RSLPStemmer()
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice')
    cursor = conexao.cursor()
    cursor.execute('SELECT idpalavra from palavras where palavra = %s', stemmer.stem(palavra))
    if cursor.rowcount > 0: retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    
    return retorno


def busca_uma_palavra(palavra):
    id_palavra = get_id_palavra(palavra)
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice')
    cursor = conexao.cursor()
    cursor.execute('SELECT urls.url from palavra_localizacao plc inner join urls on plc.idurl = urls.idurl where plc.idpalavra = %s', id_palavra)
    paginas = set()
    for url in cursor:
        paginas.add(url[0])
    for url in paginas:
        print(url)
    cursor.close()
    conexao.close()


busca_uma_palavra('python')
