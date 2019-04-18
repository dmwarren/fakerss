from . import db, fetch
import re
import json

'''
FakeRSS Instagram Plugin v0.1

I could've used someone else's Instagram scraper or an API,
but where's the fun in that?
'''


def extract_items(soup=None, url=None):
    prof_items = []
    special_chunk = False
    for chunk in soup('script'):
        try:
            if 'shortcode' in chunk.contents[0]:
                special_chunk = chunk.contents[0]
        except IndexError:
            pass  # it ain't here -- move along

    if special_chunk is False:
        raise Exception('Cannot locate shortcode bits')

    meat_json = special_chunk
    meat_json = re.sub(';$', '', meat_json)

    # remove "window._sharedData = " from giant <script> tag with latest post JSON
    meat_json = re.sub('^.* = \{', '{', meat_json)
    meat = json.loads(meat_json)

    # where the meat lives--what's a few extra nested layers of arrays between friends?
    pic_l = meat['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']

    for pic_json in pic_l:
        # trailing slash is significant
        # if picture (shortcode) URL ends with an underscore and no trailing
        # slash is present, Instagram will throw a 404
        new_url = '{0}{1}/'.format('https://www.instagram.com/p/',
                                  pic_json['node']['shortcode'])
        prof_items.append(new_url)
    return prof_items


def list_new_items(username=None, new_items=None):
    for i in new_items:
        print( '    {0}: {1}'.format(username, i))
    return


def isolate_username(url=None):
    from urllib3.util import parse_url

    # given example.com/users/123/foobar/, /return foobar (note trailing slash)
    try:
        result = parse_url(url).path.split('/')[-2]
        if len(result) < 3:
            raise Exception('Bad URL: ' + url)
        return result
    except IndexError:
        raise Exception('Bad URL: ' + url)


def digest(url=None, soup=None):
    plugin_name = 'instagram'
    # use trailing slash to avoid getting an HTTP 302
    if url[-1] != '/':
        url = url + '/'

    username = isolate_username(url)
    db_path = 'db/{0}/{1}.db'.format(plugin_name, username)
    db.create(db_path)
    soup = fetch.from_url(url)
    if soup is None:
        print('bailing!')
        return None
    live_items = extract_items(soup, url)

    new_items = []
    # do we already have some items on file?
    # no? everything is new.
    if db.file_exists(db_path) is False:
        new_items = live_items
    else:  # just the stuff we haven't recorded yet.
        new_items = db.compare(live_items, db_path)

    num_new_items = len(new_items)
    if num_new_items > 0:
        print('{0} new items found'.format(num_new_items))
        print('    {0}'.format(url))
        list_new_items(username, new_items)
        db.store_new_items(new_items, username, db_path)
    else:
        pass
    return {username: new_items}
