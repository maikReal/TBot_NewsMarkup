from xml.etree import ElementTree as ET
import requests
import config
import json
from datetime import datetime as dt


def get_xml(url):
    xml_page = requests.get(url)

    return xml_page.text


def parcing_news(xml):
    jsn = json.loads(xml)


    news_info = {'titles': [], 'urls': [], 'description': [],
                 'category': [], 'date': [], 'img': []}
    for article in jsn['articles']:


        news_info['titles'].append(article['title'].strip())
        if article['url'] is None:
            news_info['urls'].append("Sorry, we couldn't find a source for you :(")
        else:
            news_info['urls'].append(article['url'].strip())
        if article['description'] is None:
            news_info['description'].append("Sorry, we couldn't find a plot for you :(")
        else:
            news_info['description'].append(article['description'].strip())
        news_info['date'].append(article['publishedAt'].strip())
        if article['urlToImage'] is None:
            news_info['img'].append('')
        else:
            news_info['img'].append(article['urlToImage'].strip())



    return news_info

def main(keyword):
    time = dt.strftime(dt.now(), "%Y-%m-%d")
    url = 'https://newsapi.org/v2/everything?q={0}&sortBy=publishedAt&language=ru&apiKey={1}'.format(keyword, config.API_key)
    news_info = parcing_news(get_xml(url))
    length = len(news_info['titles'])
    news_info['category'].append([keyword]*length)

    return news_info
