import sys
from functools import wraps, reduce
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

from telebot.util import async_dec
import json
import re
import time
import os
import datetime
import constvar
from constvar import *
from db import *
images = []

try:
    # noinspection PyPackageRequirements,PyUnresolvedReferences
    import local
    redefined = dir(local)

    if "PROXY" in redefined:
         telebot.apihelper.proxy = local.PROXY
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


@bot.message_handler(commands=["report"])
@restricted
def cmd_report(message):
    data = select_top()
    txt = 'Timestamp\tAgent Name\tAgent Faction\tStart Level\tEnd Level\tLevel Gain\t' \
          'Start Lifetime AP\tEnd Lifetime AP\tAP Gain\t' \
          'Start Distance Walked\tEnd Distance Walked\tDistance Walked\n'
    for u in data:
        txt += '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'\
              .format(u['start']['timestamp'],
                      u['agent'],
                      factions[u['faction']],
                      u['start']['lvl'],
                      u['end']['lvl'],
                      u['end']['lvl']-u['start']['lvl'],
                      u['start']['ap'],
                      u['end']['ap'],
                      u['end']['ap'] - u['start']['ap'],
                      u['start']['trekker'],
                      u['end']['trekker'],
                      u['end']['trekker'] - u['start']['trekker'],
                      )
    bot.reply_to(message, txt)


def data_to_result(data, count=3, mod='diff_ap', team=3, cmd=False):
    d_r = []
    d_e = []
    txt = ''
    txt_r = ''
    txt_e = ''
    count = int(count)

    if len(data) < 1:
        txt = 'no data'

    d_all = sorted(data, key=lambda d_mode: d_mode[mod], reverse=True)

    for u in d_all:
        if u['faction'] == 1:
            d_r.append(u)
        if u['faction'] == 2:
            d_e.append(u)

    if team in [0, 4, 5, 6]:
        txt += RESSIGN+'+'+ENLSIGN+' Resistance + Enlightened:\n'
        for i, u in enumerate(d_all):
            if i >= count:
                break
            if cmd:
                txt += '{}: {fac}{bug}{} - {}{bug} /userid{}\n'.format(i+1, u['agent'], u[mod], u['uid'],
                                                            fac=RESSIGN if u['faction'] == 1 else ENLSIGN,
                                                             bug=BUG if u['bug'] else '')
                print(u['faction'])
            else:
                txt += '{}: {fac}{} - {}\n'.format(i+1, u['agent'], u[mod],
                                                   fac=RESSIGN if u['faction'] == 1 else ENLSIGN)
    if team in [1, 3, 4, 6]:
        txt_r += RESSIGN + 'Resistance :\n'
        for i, u in enumerate(d_r):
            if i >= count:
                break
            if cmd:
                txt_r += '{}: {bug}{} - {}{bug} /userid{}\n'.format(i + 1, u['agent'], u[mod], u['uid'],
                                                             bug=BUG if u['bug'] else '')
            else:
                txt_r += '{}: {} - {}\n'.format(i + 1, u['agent'], u[mod])
    if team in [2, 3, 5, 6]:
        txt_e += ENLSIGN + 'Enlightened:\n'
        for i, u in enumerate(d_e):
            if i >= count:
                break
            if cmd:
                txt_e += '{}: {bug}{} - {}{bug} /userid{}\n'.format(i + 1, u['agent'], u[mod], u['uid'],
                                                             bug=BUG if u['bug'] else '')
            else:
                txt_e += '{}: {} - {}\n'.format(i + 1, u['agent'], u[mod])

    return txt+txt_r+txt_e


@bot.message_handler(regexp="/(result|aresult)([\d+]?)")
@restricted
def cmd_result(message):
    count = -1
    cmd = False
    try:
        count = int(re.search('(result|aresult)(\d+)', message.text).group(2))
    except:
        pass

    try:
        if re.search('(aresult)', message.text):
            cmd = True
    except:
        pass

    if count < 3:
        count = 3

    data = select_top()
    config = get_config()
    txt = 'Лидеры по AP:\n'
    txt += data_to_result(data, count=count, cmd=cmd, team=config.result_mode)

    modes = config.modes.strip(',').lower().replace(' ', '_').split(',')
    for m in MODES:
        m_ = m.lower().replace(' ', '_')
        if m_ in modes:
            txt += '\nЛидеры по ' + m + ':\n'
            txt += data_to_result(data, count=count, mod=m_, cmd=cmd, team=config.result_mode)

    bot.send_message(message.chat.id, txt)


@bot.message_handler(commands=["showconfig"])
@restricted
def cmd_showconfig(message):
    config = get_config()
    modes = []
    for m in MODES:
        if m.lower().replace(' ', '_') in config.modes.split(','):
            modes.append(m)

    txt = 'TESTMODE: {}\n' \
          'DataTime Event: {}\n' \
          'log_chat: {}\n' \
          'result_before: {rb}\n' \
          'result_after: {ra}\n' \
          'result_mode: {rm}\n' \
          'MODES:{modes}\n' \
          '/set_modes'.\
        format('TRUE' if config.test else 'FALSE',
               'unset' if not config.data_time else itime_ctime(config.data_time),
               'unset' if not config.log_chat else config.log_chat,
               ra=config.result_after,
               rb=config.result_before,
               rm=config.result_mode,
               modes=', '.join(modes))
    bot.reply_to(message, txt)


@bot.message_handler(regexp="set_mode([\w_]+)")
@restricted
def cmd_set_modes(message):
    config = get_config()

    try:
        cmd = re.search('set_mode_([\w_]+)', message.text).group(1)
    except:
        cmd = ''

    modes = config.modes.split(',')

    txt = 'MODES: \n'
    for name in MODES:
        m = name.lower().replace(' ', '_')
        if cmd == m:
            if cmd in config.modes:
                modes.remove(cmd)
            else:
                modes.append(cmd)
        txt += '{ok}{name} /set_mode_{cmd}\n'\
            .format(name=name,
                    cmd=m,
                    ok=OK if m in modes else '')
    txt += '/showconfig'
    config.modes = ','.join(modes)
    commit()
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
    except:
        txt = 'Ошибка удаления!'
    if int(id) > -1:
        del_stata_by_id(id)
        txt = 'Статистика #statid{} удалена! #deleted\n'.format(id)
    bot.reply_to(message, txt)


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
            print(id)
            print(stat.ap)
            stat_txt = '#statid{stat.stat_id} #userid{user_id} #{agent} /userid{user_id}\n' \
                       'Timespan:{stat.timespan}\n' \
                       'faction:{fact}\n' \
                       'AP:{stat.ap}\nTrekker:{stat.trekker}\nExplorer:{stat.explorer}\n' \
                       'XM Collected:{stat.xm_collected}\n' \
                       'Builder:{stat.builder}\nConnector:{stat.connector}\nMind Controller:{stat.mind_controller}\n' \
                       'Illuminator:{stat.illuminator}\nRecharger:{stat.recharger}\nLiberator:{stat.liberator}\n' \
                       'Pioneer:{stat.pioneer}\nEngineer:{stat.engineer}\nPurifier:{stat.purifier}\n' \
                       'Portal Destroy:{stat.portal_destroy}\nLinks Destroy:{stat.links_destroy}\n' \
                       'Fields Destroy:{stat.fields_destroy}\n' \
                       'SpecOps:{stat.specops}\nHacker:{stat.hacker}\nTranslator:{stat.translator}\n' \
                       'Date_time:{date_time}\n' \
                       '{dl} STATA /delstatid{stat.stat_id}\n' \
                       '#statid{stat.stat_id} #userid{user_id} #{agent} /userid{user_id}\n' \
                .format(stat=stat, agent=stat.user.user_agent, fact=factions[stat.faction],
                        user_id=stat.user.user_id, date_time=itime_ctime(stat.data_time),
                        dl='UNDELETE' if stat.deleted else 'DELETE')
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
        user = get_user_by_id(id)
        if not (user is None):
            txt = '#userid{user_id} /userid{user_id}\nname: #{user_name}\nagentname: #{user_agent}\n'\
                .format(user_id=id, user_name=user.user_name, user_agent=user.user_agent)
            for s in user.stats:
                if ((s.data_time >= config.data_time+FS_START-config.result_before*60)
                        and (s.data_time <= config.data_time+FS_STOP+config.result_after*60)):
                    check = '✅'
                else:
                    check = ''
                txt += '#statid{stat_id} /statid{stat_id} AP:{s.ap} Trekker:{s.trekker}\n' \
                       'Timespan:{s.timespan} Date:{date_time} {check}{dl}\n'\
                    .format(stat_id=s.stat_id, s=s, date_time=itime_ctime(s.data_time),
                            check=check, dl='❌' if s.deleted else '')
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


@bot.message_handler(commands=["set_after"])
@restricted
def cmd_set_after(message):
    txt = ''
    config = get_config()
    try:
        minutes = re.search(r'(\d+)', message.text).group(0)
        print(minutes)
        config.result_after = minutes
        commit()
        txt = 'Установлено время result_after {} минут'.format(minutes)
    except (ValueError, AttributeError):
        txt = 'Не могу распознать команду, "/set_after mmm"'

    bot.reply_to(message, txt)



@bot.message_handler(commands=["set_before"])
@restricted
def cmd_set_before(message):
    txt = ''
    config = get_config()
    try:
        minutes = re.search(r'(\d+)', message.text).group(0)
        print(minutes)
        config.result_before = minutes
        commit()
        txt = 'Установлено время result_before {} минут'.format(minutes)
    except (ValueError, AttributeError):
        txt = 'Не могу распознать команду, "/set_before mmm"'

    bot.reply_to(message, txt)


@bot.message_handler(commands=["set_rm"])
@restricted
def cmd_set_result_mode(message):
    markup = InlineKeyboardMarkup()
    txt = 'Выберите режим результатов'
    for n in rm_mode:
        markup.add(InlineKeyboardButton(rm_mode[n], callback_data="set_rm {}".format(n)))
    bot.reply_to(message, txt, reply_markup=markup)


@bot.callback_query_handler(func=lambda c: 'set_rm' in c.data)
def call_back_set_rm(c):
    m = -1
    config = get_config()
    print(c.data)
    try:
        m = int(re.search(r'(\d)', c.data).group(0))
    except (ValueError, AttributeError):
        pass
    if m >= 0 and m <= 7:
        config.result_mode = m
        commit()
        txt = 'Установлен режим резкльтата {}'.format(rm_mode[m])
        bot.send_message(c.message.chat.id, txt, reply_markup=ReplyKeyboardRemove())


@bot.message_handler(commands=["setlog"])
@restricted
def cmd_setlogchat(message):
    config = get_config()

    if config.log_chat != 0 and config.log_chat != message.chat.id:
        bot.send_message(config.log_chat, "Больше я сюда не шлю логи")
    set_logchat(message.chat.id)
    bot.reply_to(message, "Теперь я буду сюда форвардить логи")


@bot.message_handler(commands=["ahelp"])
def cmd_ahelp(message):
    txt = '''
/ahelp - это меню
/help - хелп пользователей
/showconfig - посмотреть конфигурафию
/teston - включить тестовый режим
/testoff -выключит тестовый режим
/setlog - устанавливает чат для логов
/setdate - установить время ФС
/set_before - время замера до СФ
/set_after - время замера после ФС
/result - результаты
/resultXX - результаты ХХ-строчек
/aresult - результаты + cmd
/aresultXX - результаты ХХ-строчек + cmd
/set_modes - включает/выключает режимы ФС
/set_rm - выбор режима результатов
/showuserXX - посмотреть статистику агента ХХ(id в базе)
/showstatXX - посмотреть статистику ХХ (id в базе)
/delstatXX - удалить статистику ХХ (id в базе) 
'''
    bot.reply_to(message, txt)


def get_help(itime: int):
    txt = '''В *{start_count}* нужно отправить скрин с открытой медалью трекера и
*СТАТИСТИКУ* из сканера (ЧЕРЕЗ КНОПКУ КОПИРОВАТЬ В ПРОФИЛЕ).
В *{stop_count}* нужно отправить СТАТИСТИКУ ещё раз.
=================
*{start}* - Регистрация раздача плюшек и ништячков
*{start_count}* - отправка скрина и статистики агента
*{start_game}* - начало игровой части, время набора 5000 АР
*{stop_count}* - отправка скрина и статистики агента
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


@bot.message_handler(commands=["ping"])
def cmd_ping(message):
    bot.reply_to(message, 'Сам ты пинг 😐', parse_mode='Markdown')


@bot.message_handler(func=lambda message: True, content_types=["text"])
def process_msg(message):
    stata = parse_text(message)
    config = get_config()
    txt_log = ''

    if stata['success']:
        try:
            id = add_stat(message, stata)
            stat = get_stata_by_id(id)
            if ( int(time.time()) >= config.data_time+FS_START - int(config.result_before)*60
                    and int(time.time()) <= config.data_time+FS_STOP + int(config.result_after)*60):
                txt = "Агент: {}\n" \
                      "AP: {:,}\n" \
                      "Level: {}\n" \
                      "Trekker:  {:,}\n" \
                      "Период: {}\n" \
                      "Статистика добавлена #statid{}\n".format(
                    RESSIGN if stata.get('Faction') == "Resistance" else ENLSIGN + " " + stata.get('Agent', ''),
                    stata.get('AP'),
                    stata.get('Level'),
                    stata.get('Trekker', 0),
                    stata.get('Timespan'), id)
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
              time.sleep(30)