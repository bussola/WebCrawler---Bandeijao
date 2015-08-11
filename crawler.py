# This Python file uses the following encoding: utf-8
# #Esse comentario acima faz com que o python aceite UTF8
""" Este programa eh Open-source, livre para ser utilizado em quaisquer fins (Apache License)
    Para o codigo funcionar eh preciso utilizar a versao 2.7 do Python
    Este codigo utiliza o gerenciador de banco PostgreSQL, com uma unica tabela
    Dados da tabela:
    dbname='dbBandex' | user='postgres' | host='localhost' | port=5432 password='fuvest' | nome da tabela='tabela'
    A tabela contem 4 colunas: (id, dia, periodo e conteudo)
    coluna id --> integer, primary Key
    coluna dia --> text
    coluna periodo --> text
    coluna conteudo --> text

    Desenvolvido por Vinicius Magaton Bussola
"""
import requests #Requests is an Apache2 Licensed HTTP library that allow you to send HTTP/1.1 requests
from bs4 import BeautifulSoup #biblioteca para o Crawler
import psycopg2 #Biblioteca do PostgreSQL
#importe do codigo UTF-8 - Nao esta sendo utilizado
"""import sys
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')"""

#Funcao para pegar a URL
def get_soup(url):
    try:
        source_code = requests.get(url)
    except:
        return None
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)
    return soup

#Funcao para configurar o Crawler
def crawler():
    running = True
    try: #Se conecta ao Banco de dados
        conn = psycopg2.connect("dbname='dbBandex' user='postgres' host='localhost' port=5432 password='fuvest'")
    except:
        print("I am unable to connect to the database")
    cur = conn.cursor()

    cur.execute('DELETE FROM "tabela" ') #Deleta toda a tabela existente

    print("reading page.")
    soup = get_soup("http://www.ccrp.usp.br/pages/restaurante/conteudo.asp") #Encontra o site desejado
    if soup is None:
        print "Erro com o endereco da pagina"

    #Tabela principal
    table = soup.findAll('table')
    tabela = table[5]

    #Variaveis que serao usadas na tabela
    index_tabela = [4,5,7,8,10,11,13,14,16,17,19,20] #Posicoes dos  td' onde estao guardadas as informacoes no HTML
    dia_tabela = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado"]
    periodo_tabela = ["almoco", "janta"]
    index = 0 #usado como contador no while principal (vai de 0 a 11)
    dia = 0 #utilizada para pegar os dias da dia_tabela (vai de 0 a 6)
    periodo = 0 #Semelhante a variavel dia, mas para os dois periodos (vai de 0 a 1)
    tabelaID = 0 #Representa a coluna 'id' da tabela (vai de 0 ate o numero total de linhas da tabela)

    #Inicio da busca pela tabela
    while index <= 11: #Roda 12 vezes. Uma para cada periodo dos 6 dias
        conteudo = tabela.findAll('td')[index_tabela[index]]
        auxiliar = 0
        descricao_lista = [] #Array que contem o cardapio de cada dia
        while auxiliar < len(conteudo): #Este loop junta toda a informacao de um periodo do dia
            descricao_lista.append(conteudo.contents[auxiliar])
            #print conteudo.contents[auxiliar]
            auxiliar+=1
        lista = str(descricao_lista).split('<br>') #Quebra a juncao feita acima em todos '<br>'
        #print lista
        for i in lista:
            #print i
            i = str(letters(i)) #Cada item da lista eh 'filtrado' pela funcao letters
            i = i.replace("FEIJO", "FEIJÃO")       #Gambiarra para corrigir os caracteres com acento
            i = i.replace("MAA", "MAÇÃ")           #Gambiarra para corrigir os caracteres com acento
            i = i.replace("GUARNIAO", "GUARNIÇÃO") #Gambiarra para corrigir os caracteres com acento
            if len(i) == 2:
                i = i.replace("MA", "MAÇÃ")        #Gambiarra para corrigir os caracteres com acento
            if i != "":
                print str(i)
                #Preenche o Banco de Dados
                cur.execute('INSERT INTO "tabela" (id, dia, periodo, conteudo) '
                    'VALUES (%s, %s, %s, %s)', (tabelaID, dia_tabela[dia], periodo_tabela[periodo], str(i)))
                tabelaID+=1
        print "\n"
        index+=1
        if index%2 is 0: #A cada 2 'index' vira o dia
            dia+=1
        if periodo == 0: #Troca o 'periodo' entre 0 e 1
            periodo = 1
        else:
            periodo = 0
    conn.commit()

#Funcao para tirar os caracteres estranhos
def letters(input):
    valids = []
    resultado = ""
    for character in input:
        if (character.isalpha() and character.isupper()) or character == ' ' or character.isdigit() or character == ':' or character == '-': #Gambiarra para tirar o lixo
            valids.append(character)
    resultado = ''.join(valids).replace("                             ", "") #Gambiarra para tirar os espacos
    resultado = resultado.replace("  RWT  T Y N ","") #Gambiarra para tirar o lixo
    return resultado

crawler()
