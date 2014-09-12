#!/usr/bin/python

import re
import signal
import sys
import time

from requests.exceptions import ConnectionError

from kol.Session import Session
from kol.Error import Error
from kol.manager.ChatManager import ChatManager
from kol.request.GenericRequest import GenericRequest
from kol.request.GetMessagesRequest import GetMessagesRequest
from kol.request.DeleteMessagesRequest import DeleteMessagesRequest
from kol.request.CursePlayerRequest import CursePlayerRequest

# Config
_username = 'SignBot/q'
_password = ''

# Bullshit
reload(sys)
sys.setdefaultencoding('utf8')


class SignBot(object):
    def __init__(self,
                 username, password, out=sys.stdout, fmt='%Y-%m-%d %H:%M:%S',
                 caps={'sign': True, 'spider': True, 'arrow': True}):
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
            Set caps['sign'], caps['spider'], and/or caps['arrow'] to False
            (or omit them) to disable specific behaviours.

        Once the bot object is constructed, run it with go().
        """
        self.username, self.password = username, password
        self.out, self.fmt, self.caps = out, fmt, caps
        self.start, self.actions = time.time(), 0
        self.cache = {}

    def go(self):
        """
        Actually run the bot.
        """
        self.log('Logging in.')
        self.__session = Session()
        self.__session.login(self.username, self.password)
        self.__chat = ChatManager(self.__session)

        # Check pending kmails
        for kmail in self.__get_kmails():
            self.__handle_kmail(kmail)

        while True:
            for msg in self.__fetch_chat_messages():
                if msg['type'] == 'private' and self.caps.get('sign', False):
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
            time.sleep(1)

    def __del__(self):
        # Convert running time to a human-readable format
        hours, t = divmod(time.time() - self.start, 3600)
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
            duration, self.actions, 'people' if self.actions != 1 else 'person'))

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
            while limit is None or limit > 0:
                if pname is None or kmail['userName'] == pname:
                    yield kmail
                    limit -= 1

        # This is unexpected enough to crash the bot
        if pname and not len(r.responseData['kmails']):
            raise Exception("Couldn't find a kmail by {}!".format(pname))

    def __handle_kmail(self, kmail):
        if kmail['text']:
            self.log('They said: "{}"'.format(kmail['text']))
        if kmail['meat'] > 0:
            self.log('They sent {} meat.'.format(kmail['meat']))

        # Look at the items they sent
        for item in kmail['items']:
            self.log('They sent {} {}.'.format(
                item['quantity'],
                item['name'] if item['quantity'] == 1 else item['plural']))
            if item['id'] == 7698 and self.caps.get('spider', False):
                # Rubber spider
                self.__use_spider(msg['userName'], msg['userId'])
            elif item['id'] == 4939 and self.caps.get('arrow', False):
                # Time's arrow
                self.__use_arrow(msg['userName'], msg['userId'])

        # Don't keep it
        self.__del_kmail(kmail['id'])

    def __del_kmail(self, mid):
        d = DeleteMessagesRequest(self.__session, [mid])
        d.doRequest()

    def __sign(self, pname, pid):
        # "KICK ME" signs persist until rollover; SignBot does not persist
        # across rollovers.
        # If we've ever seen a player tagged, we know he'll always be tagged
        # by the same person while we exist, so we can just save that in a
        # cache.
        if pname not in self.cache:
            # Fetch user's profile page
            r = GenericRequest(self.__session)
            r.url = 'http://www.kingdomofloathing.com/showplayer.php?who={}'.format(pid)
            r.doRequest()

            # Check for the sign
            r = re.search(r'<img alt="Placed by [^"]+" title="Placed by ([^"]'
                          r'+)" style="position: absolute; left: 0px; top: 0p'
                          r'x" src="http://images.kingdomofloathing.com/other'
                          r'images/kickme.png" height="100" width="60" />',
                          r.responseText)
            if r is not None:
                self.cache[pname] = r.group(1)
        else:
            self.log("Cache hit: {} (#{})".format(pname, pid))

        if pname not in self.cache:
            resp = "You're clean."
        else:
            resp = "{} tagged you!".format(self.cache[pname])
        self.__chat_say(pname, pid, resp)
        self.actions += 1

    def __use_arrow(self, pname, pid):
        try:
            # Try to use a time's arrow on them
            c = CursePlayerRequest(self.__session, pid, 4939)
            c.doRequest()
        except Exception as e:
            # Something went wrong! Maybe they're in HC or ronin
            self.log("I couldn't use an arrow on them: {}".format(str(e)))
            self.__chat_say(pname, pid, "I couldn't use that arrow on you.")
        else:
            # Success! No need to tell them, they'll be notified
            self.log("I used an arrow on {} (#{})".format(pname, pid))
        self.actions += 1

    def __use_spider(self, pname, pid):
        try:
            # Try to use a rubber spider on them
            c = CursePlayerRequest(self.__session, pid, 7698)
            c.doRequest()
        except Exception as e:
            # Something went wrong! Maybe they're in HC or ronin
            self.log("I couldn't use a spider on {} (#{}): {}".format(
                pname, pid, str(e)))
            self.__chat_say(pname, pid, "I couldn't use that spider on you.")
        else:
            # Success! Tell them they can expect their spider
            self.log("I used a spider on {} (#{}).".format(pname, pid))
            self.__chat_say(pname, pid, "I used that spider on you.")
        self.actions += 1

    def log(self, text):
        """
        Output time-stamped text to self.out.
        """
        self.out.write('{} -- {}\n'.format(time.strftime(self.fmt), text))


if __name__ == '__main__':
    while True:
        try:
            SignBot(_username, _password).go()
        except (ConnectionError, Error) as e:
            print '{} -- Dead: {}'.format(time.strftime('%Y-%m-%d %H:%M:%S'),
                                          str(e))
            # Sleep for 10 minutes for rollover, 10 seconds otherwise
            time.sleep(600 if isinstance(e, Error) else 10)
