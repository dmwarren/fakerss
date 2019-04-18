import os
import sqlite3


def list_dir(pathname='db'):
    ''' Fetch list of files in a directory. '''
    from os import listdir
    from os.path import isfile, join
    files = [f for f in listdir(pathname) if isfile(join(pathname, f))]
    return files


def file_exists(pathname=None):
    try:
        os.stat(pathname)
        return True
    except OSError:
        return False
    return


def compare(live_items=None, db_path=None):
    '''
    IN: list of items parsed from live HTML.
    OUT: a list of objects we haven't seen before
         (compared against what's stored on disk)

    live_items == list[] of new strings.

    cheap strategy 1: table scan +
      new = list(set(live_items) - set(table_scan))

    cheap strategy 2: select() all new meat
      if it doesn't exist, it's new.
    '''
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    new_items = []
    for live_str in live_items:
        '''
        Because some users change object titles constantly to bait more clicks
        we store url::title and only search for %url% in the database.

        (does not apply to Twitter and Instagram plugins)

        Opted not to use another column because this is supposed to be a simple
        RSS-like aggregator and nobody else will ever use this anyway.
        '''
        find_str = '%{0}%'.format(live_str.split('::')[0])
        c.execute('SELECT meat FROM t_meat WHERE meat LIKE ?', (find_str,))
        result = c.fetchall()
        if len(result) < 1:  # if no matching records found
            # store the whole thing, not find_str
            new_items.append(live_str)
    return new_items


def store_new_items(new_items=None, username=None, db_path=None):
    '''
    load existing database, if any
    format incoming URLs into tuple fmt (above)
    append new tuples onto end of list
    write to disk
    '''

    from datetime import datetime
    now = datetime.now()
    dt_fmt = '{0}-{1:02d}-{2:02d}'
    dt = dt_fmt.format(now.year, now.month, now.day)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for new_str in new_items:
        c.execute('INSERT INTO t_meat VALUES (?, ?)',
                  (dt, new_str))
    conn.commit()
    conn.close()
    return


def create(db_path):
    '''
     IN: db/twitter/foo.db
    OUT: empty sqlite3 database and parent directories if necessary
    '''

    # given 'db/twitter/foo.db', isolate db/twitter/
    target_dir = 'db/{0}/'.format(db_path.split('/')[1])
    if file_exists(target_dir) is False:
        os.makedirs(target_dir)

    # creates database file if necessary
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        t_create_str = 'CREATE TABLE t_meat (datetime text, meat text)'
        idx_create_str = 'CREATE INDEX "idx_datetime" ON "t_meat" ("datetime" DESC);'
        c.execute(t_create_str)
        c.execute(idx_create_str)
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:  # already exists
        pass
    return


def get_last_timestamp(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    q = 'SELECT datetime FROM t_meat ORDER BY datetime DESC LIMIT 1;'
    c.execute(q)
    # [('2019-03-17 04:11:56',)] -- extract str
    try:
        last_timestamp = c.fetchall()[0][0]
    except IndexError:  # no results
        '''
        upstream: store everything since it's all new,
        since we have nothing yet

        yes we're using 7-bit ASCII char orders to compare date strings
        I don't care that you hate me
        this is just for entertainment; I can't be bothered to use
        datetime right now
        '''
        return '0'
    return last_timestamp


def store_new(gathered_items=None, db_path=None):
    '''
    store_new_items() without the datestamp. whoops.
    TODO: get rid of this.
    '''
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for i in gathered_items:
        c.execute('INSERT INTO t_meat VALUES (?, ?)',
                  (i[0], i[1]))  # timestamp, str
    conn.commit()
    conn.close()
    return


def read(db_path=None):
    ''' Fetch all records for `dump` utility. '''
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    q = 'SELECT datetime, meat FROM t_meat ORDER BY datetime DESC;'
    c.execute(q)
    result = c.fetchall()
    conn.close()
    return result
