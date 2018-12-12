import telegram
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler, BaseFilter
import time
import DB_actions as db
from news_gathering_script import main
from datetime import datetime
import re

"""
Ссылки выводятся плохо, потому что 1. Либо парсятся плохо 2. Либо изначально они неправильно относятся к новостям
"""

TOKEN = '716296693:AAE76_XI5J8f596xRjommGgE1GTdoWwAboU'
HELP_TEXT = '''<b>Available tags:</b>
                              \n--> <i>Sport</i>
                              \n--> <i>Economics</i>
                              \n--> <i>Politics</i>
                              \n--> <i>Science</i>
                              \n--> <i>Technology</i>
                              \n--> <i>Health</i>
                              \n--> <i>Hot</i>'''

NEWS_COUNTER_TAG = 10
NEWS_COUNTER_DATE = 10
REPLY = None
CATEGORIES = ['sport', 'economics', 'politics', 'science', 'technology', 'health', 'hot']


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def begin(bot, update):
    global HELP_TEXT
    keyboard = [[KeyboardButton('Find', callback_data='Find'),
                 KeyboardButton('Update'),
                 KeyboardButton('Add', callback_data='Add'),
                 KeyboardButton('Help')]]

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)


    text = 'Hello, my friend! \nTell me what you want!\n' + HELP_TEXT
    update.message.reply_text(text, reply_markup=reply_markup,
                              parse_mode=telegram.ParseMode.HTML)


def find(bot,update):
    global REPLY
    text = update.message.text

    if text == 'Find':
        find_news(bot, update)

    if text == 'Update':
        update_news(bot, update)

    if text == 'Help':
        global HELP_TEXT

        bot.send_message(chat_id=update.message.chat.id,
                        text=HELP_TEXT,
                        parse_mode=telegram.ParseMode.HTML)

    if text == 'Add':
        data = '''<b>Please</b>, write your news the following sequence:
             1) <b>Title</b>
             2) <b>Small plot</b>
             3) <b>Source</b>
             4) <b>Category</b>'''
        bot.send_message(chat_id=update.message.chat.id, text=data,
                     parse_mode=telegram.ParseMode.HTML)

    try:
        time = re.match(r'\d\d\d\d-\d\d-\d\d',text).group()

        find_by_time(bot, update, time)

    except AttributeError:
        False


    if '1)' in text:
        add_news(bot, update)
        print(update)

def find_by_time(bot, update, time):
    time_data = [list(i) for i in db.select_info_by_time(time)]

    time_data.reverse()

    if len(time_data) > 5:
        N = 5

        for i in range(0,N):
            try:
                bot.send_message(chat_id=update.message.chat.id, text='<b>{0}</b>\n{1}\n<b>Дата публикации:</b> {2}\n<b>Источник:</b> {3}'.format(time_data[i][0], time_data[i][2],
                                        time_data[i][3], time_data[i][4]), parse_mode=telegram.ParseMode.HTML)

            except AttributeError:
                bot.send_message(chat_id=update.callback_query.message.chat.id, text='<b>{0}</b>\n{1}\n<b>Дата публикации:</b> {2}\n<b>Источник:</b> {3}'.format(time_data[i][0], time_data[i][2],
                                        time_data[i][3], time_data[i][4]), parse_mode=telegram.ParseMode.HTML)

    if len(time_data) == 0:
        bot.send_message(chat_id=update.callback_query.message.chat.id, text='Sorry, there is no news for this date')

    if len(time_data) != 0 and len(time_data) < 5:
        N = len(time_data)
        for i in range(0,N):

            try:
                bot.send_message(chat_id=update.callback_query.message.chat.id, text='<b>{0}</b>\n{1}\n<b>Дата публикации:</b> {2}\n<b>Источник:</b> {3}'.format(time_data[i][0], time_data[i][2],
                                           time_data[i][3], time_data[i][4]), parse_mode=telegram.ParseMode.HTML)
            except AttributeError:
                bot.send_message(chat_id=update.message.chat.id, text='<b>{0}</b>\n{1}\n<b>Дата публикации:</b> {2}\n<b>Источник:</b> {3}'.format(time_data[i][0], time_data[i][2],
                                           time_data[i][3], time_data[i][4]), parse_mode=telegram.ParseMode.HTML)


def update_news(bot, update):
    keyboard = [[InlineKeyboardButton('All', callback_data='all')],
                 [InlineKeyboardButton('Sport', callback_data='sport')],
                 [InlineKeyboardButton("World", callback_data='world')],
                 [InlineKeyboardButton("Politics", callback_data='politics')],
                 [InlineKeyboardButton("Economics", callback_data='economics')],
                 [InlineKeyboardButton("Hot", callback_data='hot')],
                 [InlineKeyboardButton("Health", callback_data='health')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please, select a category:', reply_markup=reply_markup)

def add_news(bot, update):
    username = update.message.chat.username
    name = update.message.chat.first_name
    id_user = update.message.chat.id

    db.add_tagger([username, name, str(id_user)])

    time = str(datetime.now().year) + '-' + str(datetime.now().month) + '-' + str(datetime.now().day)

    data = update.message.text.split('\n')
    category = data[3].split(')')[1].strip().lower()

    if category in CATEGORIES:
        new_info = {'titles': [data[0].split(')')[1].strip()], 'urls': [data[2].split(')')[1].strip()], 'description': [data[1].split(')')[1].strip()],
                     'category': [category], 'date': [time], 'img': ['https://i.ytimg.com/vi/2giQVPIl9JM/maxresdefault.jpg']}

        db.add_news_by_other(new_info)

        bot.send_message(chat_id=update.message.chat.id, text="Your news was <b>succesfully</b> added!",
                         parse_mode=telegram.ParseMode.HTML)
    else:
        bot.send_message(chat_id=update.message.chat.id, text="I don't know such category.\nPlease, enter right category:\n<b>Sport, Economics, Politics, Science, Technology, Health, Hot</b>",
                                                            parse_mode=telegram.ParseMode.HTML)



def find_news(bot, update):
    keyboard = [[InlineKeyboardButton('By Category', callback_data='By Category'),
                 InlineKeyboardButton("By Date", callback_data='By Date')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('How do you want to find news:', reply_markup=reply_markup)

def buttons_for_finding(bot, update):

    keyboard = [[InlineKeyboardButton('Sport', callback_data='sport_find')],
                 [InlineKeyboardButton("World", callback_data='world_find')],
                 [InlineKeyboardButton("Politics", callback_data='politics_find')],
                 [InlineKeyboardButton("Economics", callback_data='economics_find')],
                 [InlineKeyboardButton("Hot", callback_data='hot_find')],
                 [InlineKeyboardButton("Health", callback_data='health_find')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_text('Please, choose a category:', reply_markup=reply_markup)

def buttons_for_time(bot, update):

    keyboard = [[InlineKeyboardButton('Today', callback_data='today_d@te')],
                 [InlineKeyboardButton("Yesterday", callback_data='yes_d@te')],
                 [InlineKeyboardButton("Own date", callback_data='own_d@te')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_text('Exactly what time:', reply_markup=reply_markup)

def button(bot, update):
    query = update.callback_query
    global REPLY
    REPLY = query.data.lower()

    if query.data == 'By Category':

        buttons_for_finding(bot, update)

    if query.data == 'By Date':
        buttons_for_time(bot, update)

    if query.data == 'today_d@te':
        tday = datetime.today()
        time = str(tday.year) + '-' + str(tday.month) + '-' + str(tday.day)

        find_by_time(bot, update, time)

    if query.data == 'yes_d@te':
        tday = datetime.today()
        time = str(tday.year) + '-' + str(tday.month) + '-' + str(tday.day-1)

        find_by_time(bot, update, time)

    if query.data == 'own_d@te':
        bot.send_message(chat_id=update.callback_query.message.chat.id, text='Please, enter a data in right format (YYYY-MM-DD):')



    if 'find' in query.data:
        word = query.data.split('_')[0]
        data_tag = [list(i) for i in db.select_info_by_tag(word)]
        data_tag.reverse()


        if len(data_tag) > 5:
            N = 5
        else:
            N = len(data_tag)

        for i in range(0,N):

            bot.send_message(chat_id=update.callback_query.message.chat.id, text='<b>{0}</b>\n{1}\n<b>Дата публикации:</b> {2}\n<b>Источник:</b> {3}'.format(data_tag[i][0], data_tag[i][2],
                                       data_tag[i][3], data_tag[i][4]), parse_mode=telegram.ParseMode.HTML)

    if query.data == 'all':
        for cat in CATEGORIES:
            data = main(cat)
            db.add_to_db(data)

        bot.send_message(chat_id=update.callback_query.message.chat_id, text='All categories was succesfully updated!')

    if query.data == 'sport':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated!'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)

    if query.data == 'science':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)

    if query.data == 'politics':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)

    if query.data == 'economics':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)

    if query.data == 'technology':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)

    if query.data == 'health':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)

    if query.data == 'hot':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)

    if query.data == 'world':
        data = main(query.data.lower())
        db.add_to_db(data)
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Category <b>{0}</b> was succesfully updated'.format(query.data),
                         parse_mode=telegram.ParseMode.HTML)


def handle_text(bot, update):
    global NEWS_COUNTER_TAG, NEWS_COUNTER_DATE, REPLY

    bot.send_chat_action(chat_id=update.message.chat.id, action=telegram.ChatAction.TYPING)

    time.sleep(2)
    if REPLY == 'By Tag':
        data_tag = [list(i) for i in db.select_info_by_tag(update.message.text)]
        data_tag.reverse()
        print(data_tag)

        N = 5
        for i in range(0,N):

            bot.send_message(chat_id=update.message.chat_id, text='<b>{0}</b>\n{1}\n<b>Дата публикации:</b> {2}\n<b>Источник:</b> {3}'.format(data_tag[i][0], data_tag[i][2],
                                       data_tag[i][3], data_tag[i][4]), parse_mode=telegram.ParseMode.HTML)




if __name__ =='__main__':
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('help', begin))
    dispatcher.add_handler(CommandHandler('start', begin))
    dispatcher.add_handler(MessageHandler(Filters.text, find))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CallbackQueryHandler(buttons_for_finding))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_text))


    updater.start_polling()