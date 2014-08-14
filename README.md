SignBot is a [Kingdom of Loathing](http://www.kingdomofloathing.com) bot.

It's initial function was to check people's profiles for ["KICK ME" signs](http://kol.coldfront.net/thekolwiki/index.php/%22KICK_ME%22_sign), but it has since gained the ability to use [rubber spiders](http://kol.coldfront.net/thekolwiki/index.php/Rubber_spider) and [time's arrows](http://kol.coldfront.net/thekolwiki/index.php/Time%27s_arrow) on people. It automatically recovers from most problems (including rollover) and logs activity to stdout.

This script powers [SignBot (#2565553)](http://127.0.0.1:60080/showplayer.php?who=2565553). If you want to run your own SignBot, you'll need Python 2.7, [`pykol`](https://github.com/scelis/pykol), [`requests`](http://docs.python-requests.org/), and to edit the `_username` and `_password` variables at the top of the script.
