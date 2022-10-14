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
    

def busca_mais_palavras(consulta):
    lista_campos = 'p1.idurl'
    lista_tabelas = ''
    lista_clausulas = ''
    palavras_id = []
    
    palavras = consulta.split(' ')
    numero_tabela = 1
    for palavra in palavras:
        id_palavra = get_id_palavra(palavra)
        if id_palavra> 0:
            palavras_id.append(id_palavra)
            if numero_tabela > 1:
                lista_tabelas += ', '
                lista_clausulas += ' AND '
                lista_clausulas += 'p%d.idurl = p%d.idurl and ' % (numero_tabela -1, numero_tabela)
            lista_campos += ', p%d.localizacao' % numero_tabela
            lista_tabelas += ' palavra_localizacao p%d' % numero_tabela
            lista_clausulas += 'p%d.idpalavra = %d' % (numero_tabela, id_palavra)
            numero_tabela += 1
    consulta_completa = 'SELECT %s FROM %s WHERE %s' %(lista_campos, lista_tabelas, lista_clausulas)
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                          port=3306, db='indice')
    cursor = conexao.cursor()
    cursor.execute(consulta_completa)
    linhas = [linha for linha in cursor]
    cursor.close()
    conexao.close()
    return linhas, palavras_id


def get_url(id_url):
    retorno = ''
    conexao = pymysql.connect(host='localhost', user='root',passwd=password_db,
                              port=3306, db='indice')
    cursor = conexao.cursor()
    cursor.execute('SELECT url from urls WHERE idurl = %s',id_url)
    if cursor.rowcount > 0: retorno = cursor.fetchone()[0]
    cursor.close()
    conexao.close()
    return retorno


#Calcula o score com base na frequencia que as palavras aparecem no documento
def frequencia_score(linhas):
    contagem = dict([linha[0], 0] for linha in linhas)
    for linha in linhas:
        contagem[linha[0]] += 1
    return contagem


# Calcula o score com base na posição das palavras no documento, quanto mais no inicio, melhor
def localizacao_score(linhas):
     localizacoes = dict([linha[0], 1000000] for linha in linhas)
     for linha in linhas:
         soma = sum(linha[1:])
         if soma < localizacoes[linha[0]]:
             localizacoes[linha[0]] = soma
     return localizacoes   


# Calcula o score com base na distancia entre as palavras, quanto menor, melhor
def distancia_score(linhas):
    if len(linhas[0]) <= 2:
        return dict([(linha[0], 1.0) for linha in linhas])
    distancias = dict([(linha[0], 1000000) for linha in linhas])
    for linha in linhas:
        distancia = sum([abs(linha[i] - linha[i - 1]) for i in range(2, len(linha))])
        if distancia < distancias[linha[0]]:
            distancias[linha[0]] = distancia
    return distancias


def pesquisa(consulta):
    linhas, palavras_id = busca_mais_palavras(consulta)
    #scores = frequencia_score(linhas)
    #scores = localizacao_score(linhas)
    scores = distancia_score(linhas)
    scores_ordenados = sorted([(score, url) for (url, score) in scores.items()], reverse = 0)
    for (score, id_url) in scores_ordenados[0:10]:
        print('%f\t%s' % (score, get_url(id_url)))
        

linhas, palavra_id = busca_mais_palavras('python programação')
pesquisa('python programação')
