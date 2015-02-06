#!/usr/bin/python
# coding=utf8

import collections
import random
import re
import signal
import sys
import time
from HTMLParser import HTMLParser

import feedparser
from requests.exceptions import ConnectionError

from kol.Session import Session
from kol.Error import Error
from kol.manager.ChatManager import ChatManager
from kol.request.GenericRequest import GenericRequest
from kol.request.GetMessagesRequest import GetMessagesRequest
from kol.request.DeleteMessagesRequest import DeleteMessagesRequest
from kol.request.CursePlayerRequest import CursePlayerRequest
from kol.request.SendMessageRequest import SendMessageRequest
from kol.request.UneffectRequest import UneffectRequest
from kol.request.UseItemRequest import UseItemRequest

# Config
_username = 'SignBot/q'
_password = ''

# Bullshit
reload(sys)
sys.setdefaultencoding('utf8')

avatar_potions = {  # potion_id: effect_id
    5841: 1098,     # A muse-bouche
    5860: 1117,     # Agent Corrigan's cigarette
    7633: 1697,     # alien hologram projector
    7604: 1668,     # artisanal hand-squeezed wheatgrass juice
    6245: 1184,     # ASCII fu manchu
    5848: 1105,     # Bangyomaman battle juice
    7631: 1695,     # black friar's tonsure
    7630: 1694,     # black magic powder
    5814: 1075,     # blob of acid
    7626: 1690,     # blue oyster badge
    5859: 1116,     # booby trap
    5854: 1111,     # BRICKO stud
    5833: 1090,     # brigand brittle
    7613: 1677,     # bubblin' chemistry solution
    5820: 1077,     # bull blubber
    7622: 1686,     # button rouge
    6241: 1180,     # censored can label
    5800: 1057,     # Charity's choker
    6247: 1186,     # cheap clip-on ninja tie
    5824: 1081,     # clove-flavored lip balm
    5845: 1102,     # compressed air canister
    6239: 1178,     # cube of ectoplasm
    7628: 1692,     # dancing fan
    6246: 1185,     # demonic surgical gloves
    7610: 1674,     # Dweebisol™ inhaler
    6242: 1181,     # ectoplasm au jus
    5799: 1056,     # eldritch dough
    7619: 1683,     # electric copperhead potion
    5836: 1093,     # embezzler's oil
    5795: 1052,     # Enchanted Flyswatter
    5806: 1063,     # enchanted muesli
    5794: 1051,     # Enchanted Plunger
    5555: 1144,     # fireclutch
    7602: 1666,     # Fitspiration™ poster
    7625: 1689,     # flask of rainwater
    5815: 1072,     # flayed mind
    5817: 1074,     # forest spirit rattle
    5821: 1078,     # frog lip-print
    5837: 1094,     # Fu Manchu Wax
    6248: 1187,     # gamer slurry
    5822: 1079,     # gazely stare
    5796: 1053,     # Gearhead Goo
    5805: 1062,     # giant breath mint
    7603: 1667,     # giant neckbeard
    5811: 1068,     # giant tube of black lipstick
    5828: 1085,     # gilt perfume bottle
    5808: 1065,     # glass of gnat milk
    5807: 1064,     # glass of warm milk
    5798: 1055,     # Gnollish Crossdress
    5842: 1099,     # gold toothbrush
    5861: 1118,     # good ash
    7632: 1696,     # government-issue identification badge
    5857: 1114,     # grey cube
    5849: 1106,     # handyman "hand soap"
    7600: 1226,     # haunted flame
    5834: 1091,     # holistic headache remedy
    5838: 1095,     # Iiti Kitty Gumdrop
    6240: 1179,     # Illuminati earpiece
    5829: 1086,     # janglin' bones
    5809: 1066,     # Knob Goblin Mutagen
    5816: 1073,     # kobold kibble
    7611: 1675,     # Lewd Lemmy Hair Oil
    6244: 1183,     # lucky cat's paw
    7624: 1688,     # lynyrd skinner toothblack
    5797: 1054,     # Missing Eye Simulation Device
    7621: 1685,     # ninja eyeblack
    7620: 1684,     # ninja fear powder
    5852: 1109,     # oil-filled donut
    5855: 1112,     # Osk'r Chow
    7629: 1693,     # page of the Necrohobocon
    5802: 1059,     # perpendicular guano
    5843: 1100,     # pirate cream pie
    7627: 1691,     # plastic Jefferson wings
    7605: 1669,     # punk patch
    7615: 1679,     # pygmy adder oil
    5831: 1088,     # pygmy dart
    5830: 1087,     # pygmy papers
    7616: 1680,     # pygmy witchhazel
    5839: 1096,     # ravenous eye
    7623: 1687,     # Red Army camouflage kit
    7609: 1673,     # Redeye™ Eyedrops
    5840: 1097,     # Rogue Windmill Rouge
    5846: 1103,     # salt water taffy
    5835: 1092,     # scrunchie tourniquet
    5856: 1113,     # Scuba Snack
    5832: 1089,     # secret mummy herbs and spices
    5804: 1061,     # Shivering Chèvre
    7617: 1681,     # short deposition
    5812: 1069,     # skelelton spine
    5827: 1084,     # skeletal banana
    5825: 1082,     # Skullery Maid's Knee
    5801: 1058,     # Smart Bone Dust
    5813: 1070,     # smut orc sunglasses
    5850: 1107,     # space marine flash grenade
    5819: 1076,     # spooky gravy fairy warlock hat
    7606: 1670,     # steampunk potion
    5853: 1110,     # stick-on gnome beard
    5818: 1075,     # Stone Golem pebbles
    7618: 1682,     # straw pole
    5810: 1067,     # Tears of the Quiet Healer
    5851: 1108,     # temporary tribal tattoo
    7601: 1665,     # temporary yak tattoo
    6243: 1182,     # the kindest cold cut
    5823: 1080,     # tiny canopic jar
    7612: 1676,     # tomato soup poster
    7608: 1672,     # turtle mud
    5844: 1101,     # una poca de gracia
    5847: 1104,     # unholy water
    7607: 1671,     # vial of swamp vapors
    7614: 1678,     # voodoo glowskull
    5858: 1115,     # votive candle
    5803: 1060,     # White Chocolate Golem Seeds
    5826: 1083,     # zombie hollandaise
}

bookkeeping = {}

class SignBot(object):
    def __init__(self,
                 username, password, out=sys.stdout, fmt='%Y-%m-%d %H:%M:%S',
                 caps={'sign': True, 'spider': True, 'arrow': True,
                       'fun': True, 'tweet': 'dril', 'avatar': True}):
        """
        username, password
            The KoL login credentials of your bot account.

        out
            Unless otherwise specified, the bot logs to sys.stdout. Provide
            an object with a write() method (like an open file) to change.
            (We won't close it.)

        fmt
            Format for the log timestamps.

        caps
            By default, the bot responds to blue messages by reporting
            "KICK ME" sign status, and to green messages by using rubber
            spiders and time's arrows contained therein.
            Set caps['sign'], caps['spider'], caps['arrow'], caps['fun'],
            caps['avatar'] to False (or omit them) to disable specific
            behaviours.
            caps['tweet'] must be a valid Twitter username or False.

        Once the bot object is constructed, run it with go().
        """
        self.username, self.password = username, password
        self.out, self.fmt = out, fmt
        self.caps = collections.defaultdict(lambda: False, caps)
        self.start = time.time()
        bookkeeping[id(self)] = [time.time(), 0]
        self.cache = {}

    def go(self):
        """
        Actually run the bot.
        """
        global active

        self.log('Logging in.')
        self.__session = Session()
        self.__session.login(self.username, self.password)
        self.__chat = ChatManager(self.__session)
        active = time.time()

        # Check pending kmails
        for kmail in self.__get_kmails():
            self.__handle_kmail(kmail)

        while True:
            if time.time() - active > 3600:
                # Chat occasionally dies quietly. Maybe that happened.
                raise Exception("Inactive for too long.")

            for msg in self.__fetch_chat_messages():
                if msg['type'] == 'private' and self.caps['sign']:
                    # Got a blue message! Report "KICK ME" sign status
                    self.log('{userName} (#{userId}) sent me '
                             'a blue message: "{text}"'.format(**msg))
                    self.__sign(msg['userName'], msg['userId'])

                elif msg['type'] == 'notification:kmail':
                    # Got a green message!
                    self.log('{userName} (#{userId}) sent me '
                             'a green message.'.format(**msg))

                    # Fetch it and examine it
                    for kmail in self.__get_kmails(msg['userName'], 1):
                        self.__handle_kmail(kmail)
                active = time.time()
            time.sleep(1)

    def __del__(self):
        # Convert running time to a human-readable format
        start, actions = bookkeeping[id(self)]
        hours, t = divmod(time.time() - start, 3600)
        minutes, seconds = divmod(t, 60)
        duration = []
        if hours:
            duration.append('{} hours'.format(int(hours)))
        if minutes:
            duration.append('{} minutes'.format(int(minutes)))
        if seconds:
            duration.append('{} seconds'.format(int(seconds)))
        if not duration:
            duration = 'a moment'
        else:
            duration = ' and '.join(duration)

        # Last words
        self.log("I existed for {}, helped {} {}, and now I am dead.".format(
            duration, actions, 'people' if actions != 1 else 'person'))
        del bookkeeping[id(self)]

    def __fetch_chat_messages(self, retry=0):
        try:
            return self.__chat.getNewChatMessages()
        except AttributeError:
            # Work around a pykol bug
            return []
        except ConnectionError:
            if retry == 3:
                raise
            self.__chat = ChatManager(self.__session)
            return self.__fetch_chat_messages(retry + 1)

    def __chat_say(self, pname, pid, text):
        self.__chat.sendChatMessage('/msg {} {}'.format(pid, text))
        self.log('I told {} (#{}) "{}"'.format(pname, pid, text))

    def __get_kmails(self, pname=None, limit=None):
        # Fetch all of our green messages
        r = GetMessagesRequest(self.__session, oldestFirst=True)
        r.doRequest()
        r.parseResponse()

        # Yield an apprioprate amount, LIFO
        for kmail in r.responseData['kmails']:
            if limit is not None and limit <= 0:
                break
            if pname is None or kmail['userName'] == pname:
                yield kmail
                if limit is not None:
                    limit -= 1

    def __handle_kmail(self, kmail):
        if kmail['text']:
            self.log('They said: "{}"'.format(kmail['text']))
        if kmail['meat'] > 0:
            self.log('They sent {} meat.'.format(kmail['meat']))
            if self.caps['tweet']:
                self.__send_kmail(kmail['userName'], kmail['userId'],
                                  tweet(self.caps['tweet']))

        # Look at the items they sent
        for item in kmail['items']:
            self.log('They sent {} {}.'.format(
                item['quantity'],
                item['name'] if item['quantity'] == 1 else item['plural']))
            if item['id'] == 7698 and self.caps['spider']:
                # Rubber spider
                self.__use_spider(kmail['userName'], kmail['userId'])
            elif item['id'] == 4939 and self.caps['arrow']:
                # Time's arrow
                self.__use_arrow(kmail['userName'], kmail['userId'])
            elif item['id'] == 4811 and self.caps['fun']:
                # Holiday Fun!
                for _ in range(item['quantity']):
                    self.__send_holiday_fun(kmail['userName'], kmail['userId'])
            elif item['id'] in avatar_potions and self.caps['avatar']:
                self.__change_avatar(item['id'],
                                     kmail['userName'], kmail['userId'])

        # Don't keep it
        self.__del_kmail(kmail['id'])

    def __del_kmail(self, mid):
        d = DeleteMessagesRequest(self.__session, [mid])
        d.doRequest()

    def __send_kmail(self, pname, pid, message, item=None):
        msg = {'userId': pid, 'text': message}
        if item:
            msg['items'] = [{'id': item, 'quantity': 1}]
        r = SendMessageRequest(self.__session, msg)
        r.doRequest()
        self.log('I sent a kmail to {} (#{}): "{}"'.format(pname, pid, message))
        if item:
            self.log('I sent them an item: {}'.format(
                {4939: "time's arrow",
                 7698: "rubber spider",
                 4811: "Holiday Fun!"}.get(item, "item #{}".format(item))))

    def __sign(self, pname, pid):
        # "KICK ME" signs persist until rollover; SignBot does not persist
        # across rollovers.
        # If we've ever seen a player tagged, we know he'll always be tagged
        # by the same person while we exist, so we can just save that in a
        # cache.
        if pname not in self.cache:
            # Fetch user's profile page
            url = 'http://www.kingdomofloathing.com/showplayer.php?who={}'.format(pid)
            profile = self.__session.opener.open(url, {}).text

            # Check for the sign
            r = re.search(r'<img alt="Placed by [^"]+" title="Placed by ([^"]'
                          r'+)" style="position: absolute; left: 0px; top: 0p'
                          r'x" src="http://images.kingdomofloathing.com/other'
                          r'images/kickme.png" height="100" width="60" />',
                          profile)
            if r is not None:
                self.cache[pname] = r.group(1)
        else:
            self.log("Cache hit: {} (#{})".format(pname, pid))

        if pname not in self.cache:
            resp = "You're clean."
        else:
            resp = "{} tagged you!".format(self.cache[pname])
        self.__chat_say(pname, pid, resp)
        bookkeeping[id(self)][1] += 1

    def __use_arrow(self, pname, pid):
        try:
            # Try to use a time's arrow on them
            c = CursePlayerRequest(self.__session, pid, 4939)
            c.doRequest()
        except Exception as e:
            # Something went wrong! Maybe they're in HC or ronin
            self.log("I couldn't use an arrow on them: {}".format(str(e)))
            try:
                self.__send_kmail(pname, pid,
                                  "I couldn't use that arrow on you, "
                                  "so I'm returning it.",
                                  4939)
            except Error as e2:
                self.log("I couldn't return their arrow: {}".format(str(e2)))
                self.__chat_say(pname, pid,
                                "I couldn't use that arrow on you and "
                                "something went wrong when I tried to "
                                "return it. Sorry!")
        else:
            # Success! No need to tell them, they'll be notified
            self.log("I used an arrow on {} (#{})".format(pname, pid))
        bookkeeping[id(self)][1] += 1

    def __use_spider(self, pname, pid):
        try:
            # Try to use a rubber spider on them
            c = CursePlayerRequest(self.__session, pid, 7698)
            c.doRequest()
        except Exception as e:
            # Something went wrong! Maybe they're in HC or ronin
            self.log("I couldn't use a spider on {} (#{}): {}".format(
                pname, pid, str(e)))
            try:
                self.__send_kmail(pname, pid,
                                  "You already have a rubber spider on you, "
                                  "so I'm returning this one.",
                                  7698)
            except Error as e2:
                self.log("I couldn't return their spider: {}".format(str(e2)))
                self.__chat_say(pname, pid,
                                "I couldn't use that spider on you and "
                                "something went wrong when I tried to "
                                "return it. Sorry!")
        else:
            # Success! Tell them they can expect their spider
            self.log("I used a spider on {} (#{}).".format(pname, pid))
            self.__chat_say(pname, pid, "I used that spider on you.")
        bookkeeping[id(self)][1] += 1

    def __send_holiday_fun(self, pname, pid):
        url = "http://www.kingdomofloathing.com/town_sendgift.php"
        data = {'whichpackage': 1,
                'towho': pid,
                'note': 'Your Holiday Fun!, courtesy of SignBot Industries.',
                'insidenote': 'Have a day.',
                'whichitem1': 4811,
                'howmany1': 1,
                'fromwhere': 0,
                'action': 'Yep.',
                'pwd': self.__session.pwd}
        resp = self.__session.opener.open(url, data)
        m = re.search(r'<table  width=95%  cellspacing=0 cellpadding=0><tr>'
                      r'<td style="color: white;" align=center bgcolor=blue'
                      r'><b>Results:</b></td></tr><tr><td style="padding: 5'
                      r'px; border: 1px solid blue;"><center><table><tr><td'
                      r'>(.*?)</td></tr></table>', resp.text)
        if m is not None and m.group(1) == 'Package sent.':
            self.log('I successfully sent {} (#{}) a plain brown wrapper '
                     'containing some Holiday Fun!'.format(pname, pid))
        else:
            err = m.group(1) if m is not None else 'Unspecified error.'
            self.__send_kmail(pname, pid,
                "I couldn't send you a gift package because of the "
                "following problem: {}".format(err), 4811)

    def __change_avatar(self, potion, pname, pid):
        try:
            # Find the IDs of the hard-shruggable effects we're under
            url = 'http://www.kingdomofloathing.com/charpane.php'
            pane = self.__session.opener.open(url, {}).text
            effects = [int(e) for e in re.findall('return hardshrug\((\d+),',
                                                  pane)]

            # Uneffect all active avatar potions
            for effect in avatar_potions.values():
                if effect in effects:
                    UneffectRequest(self.__session, effect).doRequest()
                    self.log("Uneffected ID #{}.".format(effect))

            # Use the new one and inform the person
            UseItemRequest(self.__session, potion).doRequest()
            self.log("Used avatar potion #{}.".format(potion))
            self.__chat_say(pname, pid, "Look at me!")
        except Error:
            try:
                self.__send_kmail(pname, pid,
                    "I couldn't use that avatar potion so I'm returning it.",
                    potion)
            except:
                self.__chat_say(pname, pid,
                    "I couldn't use that avatar potion and I couldn't return "
                    "it to you. Sorry.")

    def log(self, text):
        """
        Output time-stamped text to self.out.
        """
        self.out.write('{} -- {}\n'.format(time.strftime(self.fmt), text))
        self.out.flush()


def tweet(who):
    """Return a random recent tweet by the given user."""
    g = globals()
    if 'tweets' not in g or g['tweetupdate'] < time.time():
        f = feedparser.parse('http://twitrss.me/twitter_user_to_rss/?user=' + who)
        g['tweets'] = [e['summary'] for e in f['entries']]
        g['tweetupdate'] = time.time() + 3600
    return HTMLParser().unescape(random.choice(g['tweets'])).encode('latin1',
                                                                    'replace')


if __name__ == '__main__':
    while True:
        try:
            SignBot(_username, _password).go()
        except (ConnectionError, Error, Exception) as e:
            print '{} -- Dead: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'),
                                          str(e))
            sys.stdout.flush()
            if isinstance(e, Error):
                # Sleep until (probably) rollover ends
                time.sleep(600)
            else:
                time.sleep(5)
