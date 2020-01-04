import sys
from PIL import Image
from functools import wraps, reduce
import logging
import pytesseract
import telebot
from telebot.util import async_dec
import json
import re
import time
import os
import datetime
import multiprocessing
import constvar
from constvar import *
from db import *

EVENT_TIMEZONE = 'Europe/Moscow'  # Put event timezone here
API_TOKEN = ""  # Put bot token here
ADMINS = ['']  # Put telegram-names of admins here
TEST_MODE = True  # Allow send same data
UNKNOWN_AGENTS = True  # Get data from unregistered agents
MODES = ["Trekker", "Builder"]  # List medals for current event
THREAD_COUNT = multiprocessing.cpu_count()  # Count of worker threads
IMPORT_KEY = 2  # Column of telegram name in reg file
IMPORT_VAL = 1  # Column of agent name in reg file
IMPORT_DATA = {'Years': 5, 'Badges': 6}  # Columns of additional data in reg
CSV_DELIMITER = ";"
OUT_ENCODING = "cp1251"
GRADES = {}
GRADE_SIGNS = []



nextThread = 0
images = []

try:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import local
    redefined = dir(local)

    if "PROXY" in redefined:
         telebot.apihelper.proxy = local.PROXY
    if "THREAD_COUNT" in redefined:
        THREAD_COUNT = local.THREAD_COUNT
    if "EVENT_TIMEZONE" in redefined:
        EVENT_TIMEZONE = local.EVENT_TIMEZONE
    if "API_TOKEN" in redefined:
        API_TOKEN = local.API_TOKEN
    if "ADMINS" in redefined:
        ADMINS = local.ADMINS
    if "TEST_MODE" in redefined:
        TEST_MODE = local.TEST_MODE
    if "UNKNOWN_AGENTS" in redefined:
        UNKNOWN_AGENTS = local.UNKNOWN_AGENTS
    if "MODES" in redefined:
        MODES = local.MODES
    if "GRADES" in redefined:
        GRADES = local.GRADES
    if "GRADE_SIGNS" in redefined:
        GRADE_SIGNS = local.GRADE_SIGNS
    if "IMPORT_KEY" in redefined:
        IMPORT_KEY = local.IMPORT_KEY
    if "IMPORT_VAL" in redefined:
        IMPORT_VAL = local.IMPORT_VAL
    if "IMPORT_DATA" in redefined:
        IMPORT_DATA = local.IMPORT_DATA
    if "CSV_DELIMITER" in redefined:
        CSV_DELIMITER = local.CSV_DELIMITER
except ImportError:
    print("Please define data in local.py")



try:
    tzfile = open('/etc/timezone', 'r')
    LOCAL_TIMEZONE = tzfile.read().strip()
    tzfile.close()
except FileNotFoundError:
    LOCAL_TIMEZONE = EVENT_TIMEZONE


def parse_text(message):
    data = message.text

    names = constvar.names_data
    badges = constvar.badges
    lvls = constvar.badges_lvls

    lines = data.split('\n')
    if len(lines) != 2:
        bot.reply_to(message, "В сообщении должно быть две строки, не добавляйте других!")
        return {"success": False}

    (head, data) = lines
    data = data.strip().split(' ')
    print(data)
    try:
        fact_index = data.index('Enlightened')
        faction = 'Enlightened'
    except ValueError:
        try:
            fact_index = data.index('Resistance')
            faction = 'Resistance'
        except ValueError:
            return {"success": False}

    # print('fact: {}, tacr_ind: {}'.format(faction,fact_index))

    timespan = " ".join(data[0:fact_index - 1])
    data = data[fact_index - 1:]
    data.insert(0, timespan)

    print(timespan)
    head = head.replace("Unique Portals Captured", "Unique_Portals_Captured")
    for i in names.keys():
        head = head.replace(i, "_".join(i.split(' ')))

    results = {}
    head = head.strip().split(' ')

    print(head)

    print('head.len: {}, data.len: {}'.format(len(head),len(data)))

    if len(head) == len(data):
        for i in range(len(head)):
            results[names[" ".join(head[i].split('_'))]] = data[i]

    if 'AP' not in results.keys():
        print('!!!!')
        print(results.keys())
        return {"success": False}

    badge_data = [int(results['AP']), 0, 0, 0, 0, 0]
    if "Level" not in results.keys():
        try:
            for i in badges.keys():
                if i in results.keys():
                    val = int(results[i])
                    for k in range(len(badges[i])):
                        if val > badges[i][k]:
                            badge_data[k+1] += 1
        except ValueError:
            print('Error badges')
            return {"success": False}

        results['Level'] = 0
        for l in range(1, 17):
            passed = True
            for k in range(6):
                if badge_data[k] < lvls[l][k]:
                    passed = False
            if passed:
                results['Level'] = l

    results["Faction"] = faction
    results['badgeData'] = badge_data
    results['success'] = True
    results["Full"] = True
    results["mode"] = 'Full'
    return results


bot = telebot.AsyncTeleBot(API_TOKEN)


def restricted(func):
    @wraps(func)
    def wrapped(message, *args, **kwargs):
        if message.from_user.username not in ADMINS:
            bot.reply_to(message, "Нет доступа!")
            return
        return func(message, *args, **kwargs)

    return wrapped



def diff_to_txt(diff, n =3):
    txt = ''
    if len(diff) < 1:
        txt = 'no result'
    else:
        for i, d in enumerate(diff):
            if i >= n:
                break
            txt += '{}: {} +AP: {} +Trekker: {} /userid{}\n'.format(i+1, d[0], d[2], d[3],d[1])
    return txt



@bot.message_handler(commands=["report"])
@restricted
def cmd_report(message):
    txt = 'Report:\n{}'.format(select_report())
    bot.reply_to(message, txt)


@bot.message_handler(commands=["result"])
@restricted
def cmd_result(message):
    ap_r, ap_e = select_top3_facton()

    txt = 'Лидеры по AP:\nResistance:\n{}\nEnlightened:\n{}\n'.\
        format(diff_to_txt(ap_r), diff_to_txt(ap_e))
    bot.reply_to(message, txt)


@bot.message_handler(commands=["result20"])
@restricted
def cmd_result20(message):
    ap_r, ap_e = select_top3_facton()

    txt = 'Лидеры по AP:\nResistance:\n{}\nEnlightened:\n{}\n'.\
        format(diff_to_txt(ap_r, 20), diff_to_txt(ap_e, 20))
    bot.reply_to(message, txt)


@bot.message_handler(commands=["showconfig"])
@restricted
def cmd_showconfig(message):
    txt = ''
    config = get_config()

    txt = 'TESTMODE: {}\n DataTime Event: {}\n log_chat: {}'.\
        format('TRUE' if config.test else 'FALSE',
               'unset' if not config.data_time else itime_ctime(config.data_time),
               'unset' if not config.log_chat else config.log_chat)
    bot.reply_to(message, txt)


@bot.message_handler(commands=["teston"])
@restricted
def cmd_teston(message):
    set_teston()
    bot.reply_to(message, "Тестовый режим включен!")


@bot.message_handler(regexp="delstatid(\d+)")
@restricted
def cmd_delstat(message):
    id = -1
    txt = ''
    try:
        result = re.search('delstatid(\d+)', message.text)
        id = result.group(1)
        if int(id) > -1:
            del_stata_by_id(id)
        txt = 'Статистика #statid{} удалена! #deleted\n'.format(id)
    except:
        txt = 'Ошибка удаления!'
    bot.reply_to(message,txt)


@bot.message_handler(regexp="statid(\d+)")
@restricted
def cmd_showstat(message):
    id = -1
    stat_txt = ''
    try:
        result = re.search('statid(\d+)', message.text)
        id = result.group(1)
    except:
        stat_txt = 'Неправильный формат команды!'
    if int(id) > -1:
        try:
            stat = get_stata_by_id(id)
            stat_txt = '#statid{stat.stat_id} #userid{user_id} #{agent} /userid{user_id}\n' \
                       'Timespan:{stat.timespan}\n' \
                       'faction:{fact}\n' \
                       'AP:{stat.ap}\nTrekker:{stat.tracker}\nExplorer:{stat.explorer}\nXM Collected:{stat.xm}\n' \
                       'Builder:{stat.builder}\nConnector:{stat.connector}\nMind Controller:{stat.mcontroller}\n' \
                       'Illuminator:{stat.illuminator}\nRecharger:{stat.recharger}\nLiberator:{stat.liberator}\n' \
                       'Pioneer:{stat.pioneer}\nEngineer:{stat.engineer}\nPurifier:{stat.purifier}\n' \
                       'Portal Destroy:{stat.pdestroy}\nLinks Destroy:{stat.ldestroy}\nFields Destroy:{stat.fdestroy}\n' \
                       'SpecOps:{stat.specops}\nHacker:{stat.haker}\nTranslator:{stat.translator}\n' \
                       'Date_time:{date_time}\n' \
                       'DELETE STATA /delstatid{stat.stat_id}\n' \
                       '#statid{stat.stat_id} #userid{user_id} #{agent} /userid{user_id}\n' \
                .format(stat=stat, agent=stat.user.user_agent, fact=factions[stat.faction],
                        user_id=stat.user.user_id, date_time=itime_ctime(stat.data_time))
        except:
            stat_txt = 'NO STAT #statid{}'.format(id)
    else:
        stat_txt = 'NO STAT #statid{}'.format(id)
    bot.reply_to(message, stat_txt)



@bot.message_handler(regexp="userid(\d+)")
@restricted
def cmd_showuser(message):
    id = -1
    txt = ''
    config = get_config()
    try:
        result = re.search('userid(\d+)', message.text)
        id = result.group(1)
    except:
        print('command not correct')
    if int(id) > -1:
        print(id)
        user = get_user_by_id(id)
        if not (user is None):
            txt = '#userid{user_id} /userid{user_id}\n#name: {user_name}\n#agentname: {user_agent}\n'\
                .format(user_id=id, user_name=user.user_name, user_agent=user.user_agent)
            for s in user.stats:
                if ( s.data_time >= config.data_time+FS_START and s.data_time <= config.data_time+FS_STOP ):
                    check = '✅'
                else:
                    check = ''
                txt += '#statid{stat_id} /statid{stat_id} AP:{s.ap} Tracker:{s.tracker}\n' \
                       'Timespan:{s.timespan} Date:{date_time} {check}\n'\
                    .format(stat_id=s.stat_id, s=s, date_time=itime_ctime(s.data_time),
                            check=check)
        else:
            txt = 'NO USER'
    bot.send_message(message.chat.id, txt)


@bot.message_handler(commands=["testoff"])
@restricted
def cmd_testoff(message):
    config= get_config()
    set_testoff()
    bot.reply_to(message, "Тестовый режим выключен!\n"
                          "В результат попадет только статистика отправленная "
                          "в период времени\n {} - {}"
                 .format(itime_ctime(config.data_time+FS_START), itime_ctime(config.data_time+FS_STOP)))


@bot.message_handler(commands=["setdate"])
@restricted
def cmd_setdate(message):
    txt = ''
    try:
        ttime = time.strptime(re.search(r'\d\d\d\d-(\d)?\d-(\d)?\d \d\d:\d\d', message.text)
                              .group(0), '%Y-%m-%d %H:%M')
        itime = ttime_itime(ttime)
        set_datetime(itime)
        txt = 'Установлено время ФС ({})'.format(itime_ctime(itime))
    except (ValueError, AttributeError):
        txt = 'Не могу распознать дату и время, укажите в формате\n YYYY-MM-DD HH:MM"'

    config = get_config()
    bot.reply_to(message, txt)


@bot.message_handler(commands=["setlog"])
@restricted
def cmd_setlogchat(message):
    config = get_config()

    if config.log_chat != 0 and config.log_chat != message.chat.id:
        bot.send_message(config.log_chat, "Больше я сюда не шлю логи")
    set_logchat(message.chat.id)
    bot.reply_to(message, "Теперь я буду сюда форвардить логи")


def get_help(itime: int):
    txt = '''В *{start_count}* нужно отправить скрин с открытой медалью трекера и
*СТАТИСТИКУ* из клиента (ЧЕРЕЗ КНОПКУ КОПИРОВАТЬ В ПРОФИЛЕ СКАНРА).
В *{stop_count}* нужно отправить СТАТИСТИКУ ещё раз.
=================
*{start}* - Регистрация раздача плюшек и ништячков
*{start_count}* - отправка скрина статистики агента
*{start_game}* - начало игровой части, время набора 5000 АР
*{stop_count}* - отправка скрина статистики агента
*{stop_game}* - конец игровой части
*{farm_time}* - фарм ресток портала.
        '''.format(start_count=itime_hmtime(itime+int(FS_GAME)-1),
                   stop_count=itime_hmtime(itime+int(FS_GAME+FS_GAME_TIME)-1),
                   start=itime_hmtime(itime),
                   start_game=itime_hmtime(itime+int(FS_GAME)),
                   stop_game=itime_hmtime(itime+int(FS_GAME+FS_GAME_TIME)),
                   farm_time=itime_hmtime(itime+int(FARM_START))+" - "+itime_hmtime(itime+int(FARM_STOP))
                   )
    return txt


@bot.message_handler(commands=["help", "start"])
def cmd_help(message):
    config = get_config()
    txt = get_help(config.data_time)
    bot.reply_to(message, txt, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True, content_types=["text"])
def process_msg(message):
    stata = parse_text(message)
    config = get_config()
    txt_log = ''

    if stata['success']:
        try:
            id = add_stat(message, stata)
            stat = get_stata_by_id(id)
            if ( int(time.time()) >= config.data_time+FS_START and int(time.time()) <= config.data_time+FS_STOP ):
                txt = "Агент: {}\nAP: {:,}\nLevel: {}\nTrekker:  {:,}\nПериод: {}\n" \
                      "Статистика добавлена #statid{}\n".format(
                    (RESSIGN if stata.get('Faction') == "Resistance" else ENLSIGN) + " " + stata.get('Agent', ''),
                    int(stata.get('AP')), str(stata.get('Level')), int(stata.get('Trekker', 0)),
                    str(stata.get('Timespan')), id)
                txt_log = '#userid{user_id} #{user_name} /userid{user_id}\n'\
                              .format(user_id=stat.user.user_id, user_name=stat.user.user_name) + txt + ''
            else:
                print('NO TIME', config.data_time + FS_START, " ", int(time.time()))
                txt = 'Статистика ещё НЕ принимается!\n' + get_help(config.data_time)
                txt_log = '#userid{user_id}  #{user_name} /userid{user_id}\n' \
                              .format(user_id=stat.user.user_id, user_name=stat.user.user_name)
                txt_log += "Агент: {}\nAP: {:,}\nLevel: {}\nTrekker:  {:,}\nПериод: {}\n" \
                          "Статистика НЕ БУДЕТ УЧИТЫВАТЬСЯ #statid{}\n".format(
                    (RESSIGN if stata.get('Faction') == "Resistance" else ENLSIGN) + " " + stata.get('Agent', ''),
                    int(stata.get('AP')), str(stata.get('Level')), int(stata.get('Trekker', 0)),
                    str(stata.get('Timespan')), id)
        except ValueError:
            txt = 'Не могу разобрать стату, свяжитесь с организаторами!'
            txt_log += 'Стата не разобрана!!! Ошибка записи в базу.'
    else:
        txt = 'Не могу разобрать стату, свяжитесь с организаторами!'
        txt_log += 'Стата не разобрана!!! Ошибка парсинга.'

    if config.log_chat != 0:
        bot.send_message(config.log_chat, txt_log)
        bot.forward_message(config.log_chat, message.chat.id, message.message_id)
    bot.send_message(message.chat.id, "OK\n"+txt, parse_mode='Markdown')


@bot.message_handler(func=lambda message: True, content_types=["photo"])
def process_photo(message):
    # global images
    config = get_config()

    if (int(time.time()) >= config.data_time + FS_START and int(time.time()) <= config.data_time + FS_STOP):
        txt = 'Скрин принят, теперь отправь статистику.'
        txt_log = 'Агент отправил скрин.'
    else:
        print('NO TIME', config.data_time + FS_START, " ", int(time.time()))
        txt = 'Статистика ещё НЕ принимается!' + get_help(config.data_time)
        txt_log = 'Агент отправил скрин, но сейсас не время ФС'
    bot.send_message(message.chat.id, txt)
    if config.log_chat != 0:
        bot.send_message(config.log_chat, txt_log, parse_mode='Markdown')
        bot.forward_message(config.log_chat, message.chat.id, message.message_id)


def ttime_itime(ttime):
    return int(time.mktime(ttime))


def itime_ctime(itime):
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(itime))


def itime_hmtime(itime):
    return time.strftime('%H:%M', time.localtime(itime))

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except:
              print('bolt')
              logging.error('error: {}'.format(sys.exc_info()[0]))
              time.sleep(5)