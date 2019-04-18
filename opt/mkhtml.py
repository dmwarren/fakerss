#!/usr/bin/env python3

'''

mkhtml.py: a static HTML interface for FakeRSS, a minimalist system for
           scraping Twitter and other types of cancer that don't provide
           RSS feeds. (mkhtml is only designed to display Twitter content.)

Usage
-----

1. Add URLs to ../../scan.conf
2. Run FakeRSS
3. Let it populate fakerss/db/foo.db
4. Run `mkhtml.py > index.html` for pretty HTML output. Mobile-friendly, too.

Ta-da: now you have Twitter without mobille apps that control how you
interact with Twitter, inline images, ads, pop-ups*, dumb "trending"
celebrity topics, and other annoyances--all without the need to sign up
for an account.


Rage against the social media machine.


*ever visit Twitter while logged out on a mobile browser?

'''

import os
import sys
import re
import sqlite3

_link = re.compile(r'(?:(https?://)|(www\.))(\S+\b/?)([!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]*)(\s|$)', re.I)

# cheap hack to import fakersslib
sys.path.append("../../")

'''
scan db/twitter
sort filenames
for each file:
    get latest 15 entries
    {autodetect links in meat}
    print handle, timestamp\nmeat
'''
# read in list of files in db/
# sort list
SNAPSHOT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/../db/twitter'


def expiry_date():
    import datetime
    now = datetime.datetime.now() - datetime.timedelta(minutes=1700)
    dt_fmt = '{0}-{1:02d}-{2:02d}'
    dt = dt_fmt.format(now.year, now.month, now.day)
    return dt


def make_table(meat=None, username=None):
    blob = '''
<table class="table table-striped">
<tbody>
'''
    for row in meat:  # list of tuples
        # if older than 1 days, skip
        timestamp = row[0]
        handle    = row[1]
        text      = row[2]
        text = format_meat(text)
        blob += '''

<tr>
  <td valign="top">{0} &bull; <strong>{1}</strong><br />
  {2}
  </td>
</tr>
'''.format(timestamp, handle, text)

    blob += '''</tbody>
</table>
'''
    return blob


def format_meat(text=None):
    return re.sub('\\n', '<br />', text)


def get_template(filename=None):
    with open(filename, 'r') as f:
        template = f.read()
    return template


# hat tip: https://stackoverflow.com/a/17568252
def convert_links(text):
    def replace(match):
        groups = match.groups()
        protocol = groups[0] or ''  # may be None
        www_lead = groups[1] or ''  # may be None
        return '<a href="http://{1}{2}" rel="nofollow">{0}{1}{2}</a>{3}{4}'.format(
            protocol, www_lead, *groups[2:])
    return _link.sub(replace, text)


def get_recent_entries(filename=None):
    expiry_dt = expiry_date()

    username = filename.split('.')[0]
    conn = sqlite3.connect('{0}/{1}'.format(SNAPSHOT_DIR, filename))
    c = conn.cursor()
    q = 'SELECT datetime, meat from t_meat ORDER BY datetime DESC LIMIT 10'
    c.execute(q)
    results = c.fetchall()

    out_list = []
    # sneak username into the tuple
    for result in results:
        datetime = result[0]
        tweet_text = convert_links(result[1])
        if datetime < expiry_dt:
            continue
        else:
            out_list.append((result[0], username, tweet_text))
    return out_list


def main():
    snapshot_files = os.listdir(SNAPSHOT_DIR)
    header = get_template('web/header.html')
    footer = get_template('web/footer.html')
    print(header)
    meat = []
    for f in snapshot_files:
        meat.extend(get_recent_entries(filename=f))
    meat.sort(reverse=True)
    table = make_table(meat, username=f)
    print(table)
    print("<p>&nbsp;</p>")
    print(footer)


if __name__ == "__main__":
    main()
