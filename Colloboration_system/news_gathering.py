from xml.etree import ElementTree as ET
import requests


def get_xml(url):
    xml_page = requests.get(url)

    return xml_page.text


def parce_news(xml):
    tree = ET.fromstring(xml)

    news_info = {'titles': [], 'urls': [], 'description': [],
                 'category': [], 'date': []}
    for news in tree.iter('item'):
        news_info['titles'].append(news.find('title').text)
        news_info['urls'].append(news.find('link').text)
        news_info['description'].append(news.find('description').text)
        news_info['date'].append(news.find('pubDate').text)
        news_info['img'].append(news.find('enclosure').attrib['url'])

    return news_info


def main(keyword):
    # url = 'https://news.yandex.ru/%s.rss' % keyword
    url = 'https://lenta.ru/rss/news/%s' % keyword
    news_info = parce_news(get_xml(url))
    length = len(news_info['titles'])
    news_info['category'].append([keyword]*length)

    return news_info

# if __name__ == '__main__':
#     """
#     world = 'https://news.yandex.ru/world.rss'
#     index = 'https://news.yandex.ru/index.rss'
#     movies = 'https://news.yandex.ru/movies.rss'
#     music = 'https://news.yandex.ru/music.rss'
#     science = 'https://news.yandex.ru/science.rss'
#     politics = 'https://news.yandex.ru/politics.rss'
#     football = 'https://news.yandex.ru/football.rss'
#     """
#     print(len(main('world')['titles']))
