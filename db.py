import time

import sqlalchemy
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

import constvar
import local
from constvar import *

factions = constvar.factions
medal = constvar.medal

Base = declarative_base()
engine = create_engine('sqlite:///{}'.format(local.DBFILE) + '?check_same_thread=False')
session = sessionmaker(bind=engine)


class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    user_tg_id = Column(String)
    user_name = Column(String)
    user_agent = Column(String)
    user_registration_date = Column(String)
    stats = relationship("Stats", backref='users')

    def __repr__(self):
        return "id: {}, td: {}, name: {}, agent: {}, regdate: {}".\
            format(self.user_id, self.user_tg_id, self.user_name, self.user_agent, self.user_registration_date)


class Stats(Base):
    __tablename__ = "stats"
    stat_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    user = relationship("Users", uselist=False, backref='users')
    timespan = Column('Timespan', String)
    faction = Column('faction', Integer)
    ap = Column('AP', Integer)
    explorer = Column('Explorer', Integer, default=0)
    xm = Column('XM Collected', Integer, default=0)
    tracker = Column('Trekker', Integer, default=0)
    builder = Column('Builder', Integer, default=0)
    connector = Column('Connector', Integer, default=0)
    mcontroller = Column('Mind Controller', Integer, default=0)
    illuminator = Column('Illuminator', Integer, default=0)
    recharger = Column('Recharger', Integer, default=0)
    liberator = Column('Liberator', Integer, default=0)
    pioneer = Column('Pioneer', Integer, default=0)
    engineer = Column('Engineer', Integer, default=0)
    purifier = Column('Purifier', Integer, default=0)
    pdestroy = Column('Portal Destroy', Integer, default=0)
    ldestroy = Column('Links Destroy', Integer, default=0)
    fdestroy = Column('Fields Destroy', Integer, default=0)
    specops = Column('SpecOps', Integer, default=0)
    haker = Column('Hacker', Integer, default=0)
    translator = Column('Translator', Integer, default=0)
    data_time = Column(Integer)

    def __repr__(self):
        return "id: {} user:({}){}, faction: {}, ap: {}, tracker: {}, data_time: {}". \
            format(self.stat_id, self.user_id, self.user.user_agent,
                   constvar.factions.get(self.faction, ''), self.ap, self.tracker, self.data_time)


class Config(Base):
    __tablename__ = "config"
    id = Column(Integer, primary_key=True)
    test = Column(Boolean, default=False)
    data_time = Column(Integer)
    log_chat = Column(Integer, default=0)

    def __repr__(self):
        return "TEST: {}\n Date Time Event: {}\n log_chat:{}". \
            format(self.test, self.data_time, self.log_chat)


Base.metadata.create_all(bind=engine)


s = session()



def select_user_by_id_tg_agent(tg_id, agent):
    rows = s.query(Users).filter(Users.user_tg_id == tg_id, Users.user_agent == agent).all()
    result = [{'user_id': rows[i].user_id, 'user_tg_ig': rows[i].user_tg_id,
               'user_name': rows[i].user_name, 'user_agent': rows[i].user_agent,
               'user_registration_date': rows[i].user_registration_date}
              for i in range(len(rows))]
    return result


def add_user(username, tg_id, agent):
    reg_time = int(time.time())
    user = Users(
        user_name=username,
        user_tg_id=tg_id,
        user_agent=agent,
        user_registration_date=reg_time
    )
    s.add(user)
    print(user)
    s.commit()
    return user.user_id


def get_user_by_id(id: int):
    return s.query(Users).filter_by(user_id=id).first()


def get_stata_by_id(id: int):
    return s.query(Stats).filter_by(stat_id=id).first()


def del_stata_by_id(id: int):
    s.query(Stats).filter_by(stat_id=id).delete()
    s.commit()

def get_config():
    if s.query(Config).count() < 1:
        s.add(Config(test=True, data_time=0, log_chat=0))
        s.commit()
    config = s.query(Config).first()
    return config


def set_teston():
    config = get_config()
    config.test = True
    print(config.test)
    s.commit()

def set_testoff():
    config = get_config()
    config.test = False
    print(config.test)
    s.commit()

def set_datetime(itime):
    config = get_config()
    config.data_time = itime
    return s.commit()


def set_logchat(id: int):
    config = get_config()
    config.log_chat = id
    return s.commit()


def select_stata_by_agent_time(agent, stata_time):
    # rows = s.query(Stats).filter(Stats.user_id == agent, Stats.data_time == stata_time).all()
    # print(rows)
    return True


def check_stat(stata):
    fsdatatime = stata['Date'] + ' ' + stata['Time']
    print('datatime = {}'.format(fsdatatime))
    print(stata)
    stata_time = time.strptime(stata['Date'] + ' ' + stata['Time'], '%Y-%m-%d %H:%M:%S')
    print(select_stata_by_agent_time(stata['Agent'], stata_time))
    return True


def add_stat(message, stata):
    agent = stata['Agent']
    if message.forward_from:
        username = message.forward_from.username or "#" + str(message.forward_from.id)
        tg_id = message.forward_from.id
    else:
        username = message.chat.username or "#" + str(message.chat.id)
        tg_id = message.chat.id
    select_user = select_user_by_id_tg_agent(tg_id, agent)
    if len(select_user) < 1:
        print('ADD USER')
        user_id = add_user(username, tg_id, agent)
    else:
        print('USER PRESENTS')

    stata_time = time.strptime(stata['Date'] + ' ' + stata['Time'], '%Y-%m-%d %H:%M:%S')

    user = s.query(Users).filter(Users.user_tg_id == tg_id, Users.user_agent == agent).first()


    stat = Stats(
        faction=constvar.factions.get(stata['Faction'], 0),
        ap=stata['AP'],
        explorer=stata.get('Explorer', 0),
        timespan=stata['Timespan'],
        xm=stata.get('XM Collected', 0),
        tracker=stata.get('Trekker', 0),
        builder=stata.get('Builder', 0),
        connector=stata.get('Connector',0),
        mcontroller=stata.get('Mind Controller', 0),
        illuminator=stata.get('Illuminator', 0),
        recharger=stata.get('Recharger', 0),
        liberator=stata.get('Liberator', 0),
        pioneer=stata.get('Pioneer', 0),
        engineer=stata.get('Engineer', 0),
        purifier=stata.get('Purifier', 0),
        pdestroy=stata.get('Portal Destroy', 0),
        ldestroy=stata.get('Links Destroy', 0),
        fdestroy=stata.get('Fields Destroy', 0),
        specops=stata.get('SpecOps', 0),
        haker=stata.get('Hacker', 0),
        translator=stata.get('Translator', 0),
        data_time=int(time.mktime(stata_time)))

    user.stats.append(stat)
    s.commit()
    print("ADD STAT #statid{}".format(stat.stat_id))

    return stat.stat_id

def select_users():
    rows = s.query(Users).all()
    result = [{'user_id': rows[i].user_id, 'user_name': rows[i].user_name,
               'user_tg_id': rows[i].user_tg_id,
               'user_registration_date': rows[i].user_registration_date}
              for i in range(len(rows))]
    return result

def select_stats():
    rows = s.query(Stats).all()
    for row in rows:
        print('id: {} user_id: {}, datatime: {}'.format(row.stat_id, row.user_id, row.data_time))
        print(row.user.user_agent)

def get_conifg():
    config = s.query(Config).first()

def print_diff(diff, num=3):
    if len(diff) < 1:
        print('no result')
    else:
        for i, d in enumerate(diff):
            if i > num:
                pass
            print('{}: {}'.format(i+1, d))


def select_top3_facton():
    diff = []
    diff_r = []
    diff_e = []
    config = get_config()
    users = s.query(Users).all()
    # users = s.query(Users).filter(Users.stats.data_time >= FS_START and Users.stats.data_time <= FS_STOP).all()
    # int(time.time()) >= config.data_time + FS_START and int(time.time()) <= config.data_time + FS_STOP
    for user in users:
        # print(user.stats[0])
        # print(user.stats[-1])
        # print('DIFF:')

        # print('AP_diff:{} Tracker_diff:{}'.\
        #       format(diff_ap, diff_tracker))
        # diff.append((user.stats[0].faction, user.user_id, diff_ap, diff_tracker,
        #              user.stats[0].stat_id, user.stats[-1].stat_id))
        if config.test:
            try:
                diff_ap = user.stats[-1].ap - user.stats[0].ap
                diff_tracker = user.stats[-1].tracker - user.stats[0].tracker
            except:
                break
            if user.stats[0].faction == 1:
                diff_r.append((user.user_agent, user.user_id, diff_ap, diff_tracker,
                         user.stats[0].stat_id, user.stats[-1].stat_id))
            if user.stats[0].faction == 2:
                diff_e.append((user.user_agent, user.user_id, diff_ap, diff_tracker,
                         user.stats[0].stat_id, user.stats[-1].stat_id))
        else:
            stat_start = s.query(Stats)\
                .filter_by(user_id=user.user_id)\
                .filter(Stats.data_time >= config.data_time + FS_START)\
                .filter(Stats.data_time <= config.data_time + FS_STOP)\
                .order_by(Stats.data_time).first()
            stat_end = s.query(Stats) \
                .filter_by(user_id=user.user_id)\
                .filter(Stats.data_time >= config.data_time + FS_START)\
                .filter(Stats.data_time <= config.data_time + FS_STOP)\
                .order_by(Stats.data_time.desc()).first()
            # print(stat_start, '\n', stat_end)
            if stat_start is not None and stat_end is not None:
                diff_ap = stat_end.ap - stat_start.ap
                diff_tracker = stat_end.tracker - stat_start.tracker
                if user.stats[0].faction == 1:
                    diff_r.append((user.user_agent, user.user_id, diff_ap, diff_tracker,
                             stat_start.stat_id, stat_end.stat_id))
                if user.stats[0].faction == 2:
                    diff_e.append((user.user_agent, user.user_id, diff_ap, diff_tracker,
                             stat_start.stat_id, stat_end.stat_id))

    # for d in diff:
        # print(d)
    ap = sorted(diff, key=lambda d_t: d_t[2], reverse=True)
    tracker = sorted(diff, key=lambda d_t: d_t[3], reverse=True)

    ap_r = sorted(diff_r, key=lambda d_t: d_t[2], reverse=True)
    tracker_r = sorted(diff_r, key=lambda d_t: d_t[3], reverse=True)

    ap_e = sorted(diff_e, key=lambda d_t: d_t[2], reverse=True)
    tracker_e = sorted(diff_e, key=lambda d_t: d_t[3], reverse=True)

    # print('AP Resistance')
    # print_diff(ap_r)

    # print('Tracker Resistance')
    # print_diff(tracker_r)

    # print('AP Enlightened')
    # print_diff(ap_e)

    # print('Tracker Enlightened')
    # print_diff(tracker_e)

    return ap_r, ap_e


if __name__ == '__main__':
    print('RUN BASE TEST')
    print("Версия SQLAlchemy:", sqlalchemy.__version__)
    print(select_users())
    print("STATS:")
    select_top3_facton()
