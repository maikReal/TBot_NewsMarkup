import mysql.connector
import news_gathering


def connect_to_db(user, pwd, host, db):
    cnx = mysql.connector.connect(user=user, password=pwd,
                                  host=host, database=db)

    cursor = cnx.cursor()




if __name__ == '__main__':
    keyword = 'world'
    data = news_gathering.main(keyword)

