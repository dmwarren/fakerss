from bs4 import BeautifulSoup
import requests
import re
import sys
import fileinput
import importlib
from time import sleep


def dispatch(q_dict=None):
    '''
    Examine URLs in scan.conf and dynamically load relevant plugins.
    We could just have written "from . import twitter" but that's not as much fun
    '''
    for domain, scan_conf_urls in q_dict.items():
        print('Loading plugin:{0}'.format(domain))
        plugin = importlib.import_module('fakersslib.'+domain)

        for url in scan_conf_urls:
            print(url)
            plugin.digest(url=url)
            sleep(0.1)
    return


def from_file(pathname):
    ''' For development: fetch from filesystem. '''
    with open(pathname) as f:
        meat = f.read()
    soup = BeautifulSoup(meat, 'lxml')
    return soup


def from_url(url):
    ''' Fetch HTML from URL. '''
    try:
        req = requests.get(url, headers={"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6" }, allow_redirects=False)
    except requests.exceptions.ChunkedEncodingError:
        print('! connection reset')
        return None
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, 'lxml')
        return soup
    elif req.status_code == 302:
        print('! HTTP {0}'.format(req.status_code))
        return None
    elif req.status_code == 502:
        print('! HTTP {0} bad gateway'.format(req.status_code))
        return None
    elif req.status_code == 500:
        print('! HTTP 500 internal server error'.format(req.status_code))
        return None
    else:
        print('! HTTP {0}: skipping'.format(req.status_code))
        raise Exception('Not found. Update your config. Bailing.')
    return None


def scan_list(pathname='scan.conf'):
    ''' Inhale list of URLs from scan.conf. '''
    plugin_filter = None
    if len(sys.argv) > 1:
        plugin_filter = sys.argv[1]
    out_list = []
    for line in fileinput.input(pathname):
        line = line.strip()
        if len(line) < 2:                    # skip blank lines
            continue
        if re.match(r'^#', line):            # skip comments
            continue
        line = re.sub(r'\s+#.*$', '', line)  # strip inline comments
        if plugin_filter:
            if plugin_filter in line:
                out_list.append(line)
        else:  #  nofilter #wokeuplikethis
            out_list.append(line)
    out_d = collate_by_domain(out_list)
    return out_d


def collate_by_domain(in_list=None):
    '''
    IN: list of assorted URLs from scan.conf
    OUT: dict of plugins/sites, grouped together like (see below)
         to make it simpler to provide easy-to-read output.

    {'twitter': ['https://twitter.com/jsixpack',
                 'https://twitter.com/sqpublic'],
     'instagram': ['https://instagram.com/hypertalking',
                   'https://instagram.com/dinsync'],
     ... }

    '''
    from urllib3.util import parse_url
    out_d = {}

    # initialize dict keys if necessary
    # populate each k:domain with v:[list of urls]
    for url in in_list:
        # https://twitter.com/jsixpack => twitter
        plugin_name = parse_url(url).host.split('.')[-2]
        if plugin_name not in out_d:
            out_d[plugin_name] = []
        out_d[plugin_name].append(url)
    # pprint(out_d)
    return out_d
