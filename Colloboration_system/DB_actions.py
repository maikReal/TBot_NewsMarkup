import mysql.connector
import news_gathering_script
import re
import config


def add_to_db(data):
    cnx = mysql.connector.connect(user=config.user, password=config.pwd,
                                  host=config.host, database=config.db)

    cursor = cnx.cursor()

    add_news_to_db(data, cursor)

    cnx.commit()

    cursor.close()
    cnx.close()


def get_proper_name(id_news, desc, cursor):

    # finding proper names
    pattern = '\s([А-Я][А-Яа-я]+)'
    prop_names = re.findall(pattern, desc)



    # add proper names to db
    for proper_name in prop_names:

        # add to person table
        add_person = ('INSERT INTO Person '
                      '(Name) '
                      'VALUES ("{0}")'.format(proper_name))

        # proper_name = (proper_name,)
        cursor.execute(add_person)

        # get last index from person table
        query = ('SELECT MAX(ID_person) FROM Person')
        cursor.execute(query)

        last_id_person = list(map(lambda x: x[0], cursor))[0]

        # add to person_news table
        news_person = ('INSERT INTO News_Person '
                       '(ID_news, ID_person) '
                       'VALUES ({0},{1})'.format(id_news, last_id_person))

        # data_news_person = (id_news, last_id_person)
        cursor.execute(news_person)


def add_news_to_db(data, cursor):

    size = len(data['titles'])

    for i in range(size):

        # insert to table news
        add_news = ('INSERT INTO news '
                    '(Title, Image, Plot, Date)'
                    'VALUES(%s, %s, %s, %s)')

        data_news = (data['titles'][i], data['img'][i],
                     data['description'][i], data['date'][i])


        cursor.execute(add_news, data_news)

        # get last index from news table
        query = ('SELECT MAX(ID_news) FROM news')
        cursor.execute(query)

        last_id_news = list(map(lambda x: x[0], cursor))[0]


        # insert to table source
        add_source = ('INSERT INTO Source '
                      '(URL) '
                      'VALUES(%s)')

        data_source = (data['urls'][i],)
        cursor.execute(add_source, data_source)

        # get last id from source table
        query = ('SELECT MAX(ID_url) FROM Source')
        cursor.execute(query)

        last_id_source = list(map(lambda x: x[0], cursor))[0]

        # insert to news_source table
        news_source = ('INSERT INTO News_Source '
                       '(ID_news, URL) '
                       'VALUES({0},{1})'.format(last_id_news, last_id_source))

        cursor.execute(news_source)


        # insert to sphere table
        if size == 1:
            add_sphere = ('INSERT INTO Sphere '
                      '(Sphere) '
                      'VALUES ("%s")' % data['category'][i])

        else:
            add_sphere = ('INSERT INTO Sphere '
                          '(Sphere) '
                          'VALUES ("%s")' % data['category'][0][i])



        # data_sphere = (data['category'][i][0],)

        cursor.execute(add_sphere)

        # get last id from sphere table
        query = ('SELECT MAX(ID_sphere) FROM Sphere')
        cursor.execute(query)

        last_id_sphere = list(map(lambda x: x[0], cursor))[0]

        # insert to news_sphere table
        news_sphere = ('INSERT INTO News_Sphere '
                       '(ID_news, Sphere) '
                       'VALUES ({0},{1})'.format(last_id_news, last_id_sphere))

        # data_news_sphere = (last_id_news, last_id_sphere)

        cursor.execute(news_sphere)

        # add to person table
        get_proper_name(last_id_news, data['titles'][i], cursor)



def add_tagger(data):
    cnx = mysql.connector.connect(user=config.user, password=config.pwd,
                                  host=config.host, database=config.db)

    cursor = cnx.cursor()

    # добавление в БД информацию о юзере
    add_tagger = ('INSERT INTO Tagger '
                      '(Nickname, Name, Profile_link) '
                      'VALUES ("%s", "%s", "%s")' % (data[0], data[1], data[2]))


    cursor.execute(add_tagger)
    cnx.commit()

    cursor.close()
    cnx.close()



def add_news_by_other(data):
    cnx = mysql.connector.connect(user=config.user, password=config.pwd,
                                  host=config.host, database=config.db)

    cursor = cnx.cursor()


    add_news_to_db(data, cursor)

    # выбираем последнюю запись в бд, чтобы соединить ее через другую таблицу
    query = ('SELECT MAX(ID_nickname) FROM Tagger')
    cursor.execute(query)

    last_id_tagger = list(map(lambda x: x[0], cursor))[0]

    # получаем последнюю новость
    query = ('SELECT MAX(ID_news) FROM news')
    cursor.execute(query)

    last_id_news = list(map(lambda x: x[0], cursor))[0]

    # добавление в таблицу News_Tagger
    news_tagger = ('INSERT INTO News_Tagger '
                       '(ID_news, Nickname) '
                       'VALUES ({0},{1})'.format(last_id_news, last_id_tagger))

    cursor.execute(news_tagger)


    cnx.commit()

    cursor.close()
    cnx.close()

def select_info_by_time(time):
    cnx = mysql.connector.connect(user=config.user, password=config.pwd,
                                  host=config.host, database=config.db)

    cursor = cnx.cursor(buffered=True)

    query = "select n.Title, n.Image, n.Plot, n.Date, Source.URL, Sphere.Sphere from news n inner join News_Source on n.Id_news=News_Source.Id_news inner join Source on Source.ID_url=News_Source.URL inner join News_Sphere on n.Id_news=News_Sphere.ID_news inner join Sphere on News_Sphere.Sphere=Sphere.ID_sphere where n.Date like '%{0}%'".format(time)

    cursor.execute(query)

    data_news_by_time = []
    for news in cursor:
        data_news_by_time.append(news)

    cnx.commit()

    cursor.close()
    cnx.close()

    return data_news_by_time

def select_info_by_tag(tag):
    cnx = mysql.connector.connect(user=config.user, password=config.pwd,
                                  host=config.host, database=config.db)

    cursor = cnx.cursor(buffered=True)



    # can write Category if i want
    query = "select n.Title, n.Image, n.Plot, n.Date, Source.URL, Sphere.Sphere from news n inner join News_Source on n.Id_news=News_Source.Id_news inner join Source on Source.ID_url=News_Source.URL inner join News_Sphere on n.Id_news=News_Sphere.ID_news inner join Sphere on News_Sphere.Sphere=Sphere.ID_sphere where Sphere.Sphere='{0}'".format(tag)

    cursor.execute(query)

    data_news_by_tag = []
    for news in cursor:
        data_news_by_tag.append(news)

    cnx.commit()

    cursor.close()
    cnx.close()

    return data_news_by_tag

