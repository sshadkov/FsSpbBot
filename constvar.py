RESSIGN = "💙"
ENLSIGN = "💚"
OK = "✅"
BUG = '🐞'

FS_GAME = +1*60*60   # время замера 1 час
FS_GAME_TIME = 2*60*60
FS_START = FS_GAME  # за 10 минут начать принимать скрины
FS_STOP = FS_GAME+FS_GAME_TIME
FARM_START = FS_GAME+FS_GAME_TIME+30*60
FARM_STOP = FS_GAME+FS_GAME_TIME+60*60

rm_mode = {0: RESSIGN + ENLSIGN,
           1: RESSIGN,
           2: ENLSIGN,
           3: RESSIGN + ' + ' + ENLSIGN,
           4: RESSIGN + ENLSIGN + ' + ' + RESSIGN,
           5: RESSIGN + ENLSIGN + ' + ' + ENLSIGN,
           6: RESSIGN + ENLSIGN + ' + ' + RESSIGN + ' + ' + ENLSIGN,
           }

apgains = {
        "Builder": (65, 150, 375),
        "Hacker": (0, 50, 400),
        "Mind Controller": (1250, 1250, 1250),
        "Liberator": (500, 500, 500),
        "Purifier": (75, 75, 75),
        "Links Destroy": (187, 187, 187),
        "Fields Destroy": (750, 750, 750),
        "Engineer": (125, 125, 125),
        "Translator": (0, 50, 0)
    }

MODES = ["Explorer", "XM Collected", "Trekker", "Builder", "Connector", "Mind Controller", "Illuminator",
"Recharger", "Liberator", "Pioneer", "Engineer", "Purifier", "Portal Destroy", "Links Destroy", "Fields Destroy",
"SpecOps", "Hacker", "Translator"]



names_data = {
    'Time Span': 'Timespan',
    'Agent Name': 'Agent',
    'Agent Faction': 'Faction',
    'Date (yyyy-mm-dd)': 'Date',
    'Time (hh:mm:ss)': 'Time',
    'Lifetime AP': 'TotalAP',
    'Current AP': 'AP',
    'Unique Portals Visited': 'Explorer',
    'Portals Discovered': 'Seer',
    'Seer Points': 'SeerP',
    'XM Collected': 'XM Collected',
    'OPR Agreements': 'OPR',
    'Distance Walked': 'Trekker',
    'Resonators Deployed': 'Builder',
    'Links Created': 'Connector',
    'Control Fields Created': 'Mind Controller',
    'Mind Units Captured': 'Illuminator',
    'Longest Link Ever Created': 'none',
    'Largest Control Field': 'none',
    'XM Recharged': 'Recharger',
    'Unique Portals Captured': 'Pioneer',
    'Portals Captured': 'Liberator',
    'Mods Deployed': 'Engineer',
    'Resonators Destroyed': 'Purifier',
    'Portals Neutralized': 'Portal Destroy',
    'Enemy Links Destroyed': 'Links Destroy',
    'Enemy Fields Destroyed': 'Fields Destroy',
    'Max Time Portal Held': 'Guardian',
    'Max Time Link Maintained': 'none',
    'Max Link Length x Days': 'none',
    'Max Time Field Held': 'none',
    'Largest Field MUs x Days': 'none',
    'Unique Missions Completed': 'SpecOps',
    'Hacks': 'Hacker',
    'Glyph Hack Points': 'Translator',
    'Longest Hacking Streak': 'Sojourner',
    'Agents Successfully Recruited': 'Recruiter',
    'Mission Day(s) Attended': 'MD',
    'NL-1331 Meetup(s) Attended': 'NL',
    'First Saturday Events': 'FS',
    'Clear Fields Events': 'ClearField',
    'Prime Challenges': 'Prime',
    'Stealth Ops Missions': 'Stealth',
    'OPR Live Events': 'OPR',
    'Level': 'Level',
    'Recursions': 'Recursions',
    'Umbra: Unique Resonator Slots Deployed': 'Umbra',
    'Links Active': 'none',
    'Portals Owned': 'none',
    'Control Fields Active': 'none',
    'Mind Unit Control': 'none',
    'Current Hacking Streak': 'none',
    'Didact Fields Created': 'Didact'
}


factions = {
    'Unknown': 0,
    'Resistance': 1,
    'Enlightened': 2,
    0: 'Unknown',
    1: 'Resistance',
    2: 'Enlightened',
}

medal = {
    0: "Explorer",
    1: "XM Collected",
    2: "Trekker",
    3: "Builder",
    4: "Connector",
    5: "Mind Controller",
    6: "Illuminator",
    7: "Recharger",
    8: "Liberator",
    9: "Pioneer",
    10: "Engineer",
    11: "Purifier",
    12: "Portal Destroy",
    13: "Links Destroy",
    14: "Fields Destroy",
    15: "SpecOps",
    16: "Hacker",
    17: "Translator", }

badges = {
    'NL': (1, 5, 10, 25, 50),
    'Guardian': (3, 10, 20, 90, 150),
    'Recruiter': (2, 10, 25, 50, 100),
    'Explorer': (100, 1000, 2000, 10000, 30000),
    'Connector': (50, 1000, 5000, 25000, 100000),
    'Pioneer': (20, 200, 1000, 5000, 20000),
    'Hacker': (2000, 10000, 30000, 100000, 200000),
    'Trekker': (10, 100, 300, 1000, 2500),
    'Recharger': (100000, 1000000, 3000000, 10000000, 25000000),
    'Translator': (200, 2000, 6000, 20000, 50000),
    'Illuminator': (5000, 50000, 250000, 1000000, 4000000),
    'Engineer': (150, 1500, 5000, 20000, 50000),
    'Builder': (2000, 10000, 30000, 100000, 200000),
    'Purifier': (2000, 10000, 30000, 100000, 300000),
    'SpecOps': (5, 25, 100, 200, 500),
    'Liberator': (100, 1000, 5000, 15000, 40000),
    'Sojourner': (15, 30, 60, 180, 360),
    'Mind Controller': (100, 500, 2000, 10000, 40000),
    'FS': (1, 6, 12, 24, 36),
    'MD': (1, 3, 6, 10, 20),
    'Prime': (1, 2, 3, 4, 1000),
    'Stealth': (1, 3, 6, 10, 20),
    'ClearField': (1, 3, 6, 10, 20)
}


badges_lvls = {
    1: (0, 0, 0, 0, 0, 0),
    2: (2500, 0, 0, 0, 0, 0),
    3: (20000, 0, 0, 0, 0, 0),
    4: (70000, 0, 0, 0, 0, 0),
    5: (150000, 0, 0, 0, 0, 0),
    6: (300000, 0, 0, 0, 0, 0),
    7: (600000, 0, 0, 0, 0, 0),
    8: (1200000, 0, 0, 0, 0, 0),
    9: (2400000, 0, 4, 1, 0, 0),
    10: (4000000, 0, 5, 2, 0, 0),
    11: (6000000, 0, 6, 4, 0, 0),
    12: (8400000, 0, 7, 6, 0, 0),
    13: (12000000, 0, 0, 7, 1, 0),
    14: (17000000, 0, 0, 0, 2, 0),
    15: (24000000, 0, 0, 0, 3, 0),
    16: (40000000, 0, 0, 0, 4, 2),
}



def test():
    print('Добрый день!')
    pass


if __name__ == '__main__':
    test()
