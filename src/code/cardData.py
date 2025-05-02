import mysql.connector
import cardSet
import pokedex
import evolutionsSet
import imagehash
import numpy as np

username = "root"  # Seu nome de usuário do MySQL
password = "26ot2001"  # Sua senha do MySQL
databasename = "pokemonDatabase"  # Nome do banco de dados que queremos criar


# Cria um banco de dados de Pokémon
def createDatabase():
    # Conecta ao localhost
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password
    )

    # Cria um cursor para que possamos criar bancos de dados
    mycursor = db.cursor()

    # Verifica se o banco de dados já foi criado; se não, cria um novo
    mycursor.execute(
        "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{}'".format(databasename))
    if mycursor.fetchone() is None:
        mycursor.execute(f"CREATE DATABASE {databasename}")
    else:
        # Caso o usuário tenha esquecido de alterar a configuração após já ter criado o banco de dados
        mycursor.execute(f"DROP DATABASE {databasename}")  
        mycursor.execute(f"CREATE DATABASE {databasename}")

    # Adiciona tabelas e valores ao banco de dados
    initializeDatabase()


# Inicializa o banco de dados com valores iniciais para cartas e Pokémon
def initializeDatabase():
    # Conecta ao banco de dados que já existia ou foi criado em createDatabase()
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=databasename
    )

    # Cria um cursor para que possamos editar o banco de dados
    mycursor = db.cursor()

    # Cria um objeto Pokedex que contém informações sobre os primeiros 151 Pokémon (Kanto) e algumas mega evoluções
    # As informações incluem número da Pokédex, nomes dos Pokémon, tipo, estágio e altura
    poke = pokedex.Pokedex()

    # Cria um objeto CardSet que contém informações sobre as cartas da coleção Evolutions
    # As informações incluem números das cartas, nomes dos Pokémon, nomes das cartas, raridade e tipo da carta
    evoSet = cardSet.CardSet()

    # Cria um objeto EvolutionsSet que armazena os hashes das imagens das cartas de Pokémon
    # Contém hashes para as seguintes orientações da carta: normal, espelhada, de cabeça para baixo e invertida espelhada
    evoCards = evolutionsSet.EvolutionsSet()

    # Cria uma nova tabela "Pokemon" que armazenará os valores do objeto poke (Pokédex)
    mycursor.execute("CREATE TABLE Pokemon (dexNumber SMALLINT, pokemon VARCHAR(20) PRIMARY KEY, \
            poketype VARCHAR(10), height DOUBLE UNSIGNED, stage VARCHAR(5))")

    # Popula a tabela "Pokemon"
    for x in range(poke.numpoke):
        mycursor.execute("INSERT INTO Pokemon (dexNumber, pokemon, poketype, stage, height) VALUES(%s, %s, %s, %s, %s)",
                         (poke.dexnumber[x], poke.pokemon[x], poke.type[x], poke.stage[x], poke.height[x]))

    # Cria uma nova tabela "EvolutionsSet" que armazenará os valores do objeto evoSet (conjunto de cartas)
    mycursor.execute("CREATE TABLE EvolutionsSet (cardnumber TINYINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, \
            cardname VARCHAR(50), pokemon VARCHAR(20), rarity VARCHAR(13), cardtype VARCHAR(17))")

    # Popula a tabela "EvolutionsSet"
    for x in range(evoSet.numCards):
        mycursor.execute("INSERT INTO EvolutionsSet (cardname, pokemon, rarity, cardtype) VALUES(%s, %s, %s, %s)",
                         (evoSet.cardnamelist[x], evoSet.pokemonlist[x], evoSet.rarity[x], evoSet.cardtype[x]))

    # Cria uma nova tabela "EvolutionsCards" que armazenará os valores do objeto evoCards (conjunto de hashes das cartas)
    mycursor.execute("CREATE TABLE EvolutionsCards (cardnumber TINYINT UNSIGNED PRIMARY KEY AUTO_INCREMENT, \
            FOREIGN KEY(cardnumber) REFERENCES EvolutionsSet(cardnumber), \
            avghashes VARCHAR(20), avghashesmir VARCHAR(20), avghashesud VARCHAR(20), avghashesudmir VARCHAR(20), \
            whashes VARCHAR(20), whashesmir VARCHAR(20), whashesud VARCHAR(20), whashesudmir VARCHAR(20), \
            phashes VARCHAR(20), phashesmir VARCHAR(20), phashesud VARCHAR(20), phashesudmir VARCHAR(20), \
            dhashes VARCHAR(20), dhashesmir VARCHAR(20), dhashesud VARCHAR(20), dhashesudmir VARCHAR(20))")

    # Popula a tabela "EvolutionsCards"
    for x in range(evoCards.setSize):
        mycursor.execute(
            "INSERT INTO EvolutionsCards (avghashes, avghashesmir, avghashesud, avghashesudmir, \
            whashes, whashesmir, whashesud, whashesudmir, \
            phashes, phashesmir, phashesud, phashesudmir, \
            dhashes, dhashesmir, dhashesud, dhashesudmir) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (evoCards.hashes[x][0], evoCards.hashesmir[x][0], evoCards.hashesud[x][0], evoCards.hashesudmir[x][0],
             evoCards.hashes[x][1], evoCards.hashesmir[x][1], evoCards.hashesud[x][1], evoCards.hashesudmir[x][1],
             evoCards.hashes[x][2], evoCards.hashesmir[x][2], evoCards.hashesud[x][2], evoCards.hashesudmir[x][2],
             evoCards.hashes[x][3], evoCards.hashesmir[x][3], evoCards.hashesud[x][3], evoCards.hashesudmir[x][3]))

    # Confirma as mudanças no banco de dados
    db.commit()


# Retorna um dicionário com os valores da carta Pokémon correspondente se a distância do hash estiver dentro do limite
# Se nenhuma carta correspondente for encontrada, retorna None
def compareCards(hashes):
    cutoff = 18  # Valor limite arbitrário definido através de testes
    # Conecta ao banco de dados das cartas de Pokémon
    db = mysql.connector.connect(
        host="localhost",
        user=username,
        passwd=password,
        database=databasename
    )

    mycursor = db.cursor(buffered=True)  # Cria um cursor com buffered=True para evitar mycursor.rowcount retornar 0

    mycursor.execute("SELECT * FROM EvolutionsCards")  # Obtém valores da tabela EvolutionsCards (hashes)

    # Cria arrays para armazenar as diferenças de hash para cada orientação; cada método de hashing tem seu próprio array
    avghashesDists = np.zeros(4)
    whashesDists = np.zeros(4)
    phashesDists = np.zeros(4)
    dhashesDists = np.zeros(4)

    maxHashDists = []  # Lista para armazenar o maior valor da menor diferença de hash para cada carta

    for _ in range(mycursor.rowcount):  # Percorre cada linha da tabela EvolutionsCards
        # Obtém os valores armazenados em cada linha
        cardnum, avghash1, avghash2, avghash3, avghash4, \
        whash1, whash2, whash3, whash4, \
        phash1, phash2, phash3, phash4, \
        dhash1, dhash2, dhash3, dhash4 = mycursor.fetchone()

        # Converte cada hash de String para hash e calcula a distância em relação à imagem escaneada
        avghashesDists[0] = hashes[0] - imagehash.hex_to_hash(avghash1)
        whashesDists[0] = hashes[1] - imagehash.hex_to_hash(whash1)
        phashesDists[0] = hashes[2] - imagehash.hex_to_hash(phash1)
        dhashesDists[0] = hashes[3] - imagehash.hex_to_hash(dhash1)

        # Calcula a menor diferença de cada método de hash e armazena o maior desses valores
        maxHashDists.append(max([min(avghashesDists), min(whashesDists), min(phashesDists), min(dhashesDists)]))

    if min(maxHashDists) < cutoff:
        return {'Pokemon': 'Correspondente encontrado'}
    return None

