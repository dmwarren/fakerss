from bs4 import BeautifulSoup, NavigableString
from . import db, fetch
from datetime import datetime
import fileinput
import re
from textwrap import TextWrapper
from twitter_scraper import get_tweets

'''
FakeRSS Twitter Plugin v0.1.

Tried writing my own scraper but gave up.
https://pypi.org/project/twitter-scraper brings the world to YOU in a dict.

Thank you, Kenneth Reitz!

{'tweetId': '986728649167720448',
 'time': datetime.datetime(2018, 4, 18, 15, 10, 17),
 'text': "That kid on the sofa couldn't handle the excitement of 90s edutainment.pic.twitter.com/qLHkGg8xwR",
 'replies': 194,
 'retweets': 1768,
 'likes': 7185,
 'entries': {'hashtags': [],
  'urls': [],
  'photos': ['https://pbs.twimg.com/media/DbGQbRmX4AcT0wa.jpg'],
  'videos': []}}

Pro: I don't have to deal with 14 different tweet object formats
(pictures, movies, retweets, polls, ...).

Con: Retweets are not attributed to the original author which can be
confusing. Oh well, it's Twitter so it's 99% worthless misinformation
anyway, right?

Not like Twitter is an appropriate forum for customer service or long-form
discussions and formal political discourse... right? Ha! Haha!
hahahahahaha<uncontrollable sobbing>

'''


def extract_items(username=None):
    prof_items = []
    for tweet in get_tweets(username, pages=1):
        timestamp = humanize_timestamp(tweet['time'])
        meat = cleanup(tweet)
        prof_items.append((timestamp, meat))
    return prof_items


def cleanup(meat=None):
    # IN: Raw Twitter library output.
    # OUT: Complete picture and video URLs without redundant links.

    # pic.twitter.com URLs are just shortened links/redirects.
    # These are redundant now that Kenneth Reitz hands you the
    # actual picture URL in a dict, so nuke 'em.
    out_str = re.sub("pic.twitter.com/\w+", ' ',
                     meat['text'], flags=re.MULTILINE)
    if len(meat['entries']['photos']) > 0:
        photo_urls = "\n".join(meat['entries']['photos'])
        out_str += "\n" + photo_urls
    if len(meat['entries']['videos']) > 0:
        '''
        'videos': [{'id': 'gv-GU1gUl9RjW4j_'}]
        it's a list? potentially more than one? okay...
        no idea if it'll be more entries in the same dict or more
        items in a list. so let's pick something.
        that will guarantee the outcome is the opposite of
        what I programmed for.
        '''
        for video in meat['entries']['videos']:
            out_str += "\n" + video['id']
    return out_str.strip()


def regex_filter(new_items=None):
    '''
    IN: [('date_str', 'tweet_txt'), ...]
    OUT: Same list, but without the tuples that trip filter.txt
    '''
    out_list = []

    # inhale filter list
    patterns = []
    for line in fileinput.input('filter.conf'):
        line = line.strip()
        # multi-plugin filter file, so strip twitter: prefix from each pattern
        line = re.sub('^twitter:', '', line)
        # skip blank lines
        if len(line) < 3:
            continue
        # skip comments
        if re.match(r'^#', line):
            continue
        patterns.append(line)
    combined_re = "(" + ")|(".join(patterns) + ")"
    compiled_re = re.compile(combined_re, flags=re.MULTILINE)

    if len(patterns) == 0:
        # no filters found
        return new_items

    for tweet_tpl in new_items:
        if compiled_re.match(tweet_tpl[1]):
            pass
        else:
            out_list.append(tweet_tpl)

    return out_list


def humanize_timestamp(in_datetime=None):
    # convert seconds since the Unix epoch to something readable
    return datetime.strftime(in_datetime, '%Y-%m-%d %H:%M:%S')


def list_new(username=None, new_items=None):
    '''
    split meat by newlines and process/display them chunk by chunk
    to avoid this:  (example tweet displayed in CLI)

    This format was announced in 2000 and similarly decreased the pit
    sizes as well as packing the pits closer together.
It uses the               <== GRRRRRRR
    same 780 nm infrared laser as a standard CD, so it's not like DVD
    tech which switches to a 650 nm red laser.
    '''
    spaces = 4
    indent = ' ' * spaces
    wrapper = TextWrapper(initial_indent=indent,
                          subsequent_indent=indent,
                          replace_whitespace=False,
                          width=70)
    for i in new_items:
        timestamp = i[0]
        all_lines = i[1]
        chunks = all_lines.split("\n")

        print('{0} - {1}'.format(username, timestamp))
        for sentence in chunks:
            for line in wrapper.wrap(sentence):
                print(line)
        print('-' * 70)
    return


def isolate_username(url=None):
    from urllib3.util import parse_url
    # given http://twitter.com/foobar, return foobar
    try:
        result = parse_url(url).path.split('/')[-1]
        if len(result) < 3:
            raise Exception('Bad URL: ' + url)
        return result
    except IndexError:
        raise Exception('Bad URL: ' + url)


def digest(url=None, soup=None):
    plugin_name = 'twitter'
    username = isolate_username(url)
    db_path = 'db/{0}/{1}.db'.format(plugin_name, username)
    db.create(db_path)
    live_items = extract_items(username)
    new_items = []

    # do we already have some items on file?
    # no? everything is new.
    if db.file_exists(db_path) is False:
        new_items = live_items
    else:  # just the stuff we haven't recorded yet.
        last_timestamp = db.get_last_timestamp(db_path)
        new_items = isolate_new(live_items, last_timestamp)

    # filter.txt processing
    # We do this /here/ as a lazy way to avoid dealing with
    # returning None all the back up the chain.
    new_items = regex_filter(new_items)
    num_new_items = len(new_items)

    if num_new_items > 0:
        list_new(username, new_items)
        db.store_new(new_items, db_path)
    return {username: new_items}


def isolate_new(live_items=None, last_timestamp=None):
    '''
    compare date strings. yes, strings.

    this is a cheap ASCII character-order comparison but
    it's good enough for my purposes.
    '''
    new_items = []
    for tweet in live_items:
        # tuple: (date, tweet text)
        if tweet[0] > last_timestamp:
            new_items.append(tweet)
    return new_items
