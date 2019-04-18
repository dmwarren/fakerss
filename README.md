# FakeRSS
A simple system for aggregating new stuff from websites that don't provide RSS feeds, complete with command-line reader and web interface. Logs new items to a SQLite3 database. Includes plugins for Twitter and Instagram.


# ... but why?

Social media is cancer but unfortunately there is also some nice retrocomputing, Python, and other geek stuff flying through it. I want the good stuff without a mobile app (or worse, a mobile app's crappy website--with popups!) controlling how I consume it. 

Plus, I don't want to sign up for an account on *any* of these services. I just want new links once or twice a day, on the command line, with no distractions.

Rage against the social media machine. Bring back the decentralized web!


# Installation
  - pip3 install --user -r requirements.txt
  - edit scan.conf
  - chmod +x fakerss
  - ./fakerss

# Limitations
  - Retweets are not attributed to their original author. Oh well. Twitter is mostly garbage anyway, right?

# License
Please see LICENSE.md.

# Version History
  - 17-Apr-2019 - v0.20 - First public release
  - 25-Dec-2016 - v0.01 - First working version

Blame warren@sfu.ca.

# In Action

```
$ ./fakerss

Loading plugin:twitter
https://twitter.com/foone
foone - 2019-04-17 17:55:30
    but some smartsases figured out it was cheaper to buy an old one
    from the 80s (because Model M keyboards do not die) and rip out
    the controller board and stuff in a replacement. Bam, you've got a
    Model M on your macbook and it's only like 50$!
----------------------------------------------------------------------
https://twitter.com/a2_4am
a2_4am - 2019-04-17 15:01:34
    Then there was the whole thing where bit copier developers were so
    scared of being sued and/or arrested that Locksmith 1–4 embedded
    your serial number in every copy it produced so they could assist
    in investigating piracy. (No one ever asked.)
----------------------------------------------------------------------
a2_4am - 2019-04-16 15:35:48
    You're not out of bytes until qkumba says you're out of bytes.
----------------------------------------------------------------------
Loading plugin:instagram
https://www.instagram.com/nyccatsitter
2 new items found
    https://www.instagram.com/nyccatsitter/
    nyccatsitter: https://www.instagram.com/p/BwYC8QuB6z6/
    nyccatsitter: https://www.instagram.com/p/BwSZLzlhS1x/
https://www.instagram.com/unitofcat
1 new items found
    https://www.instagram.com/unitofcat/
    unitofcat: https://www.instagram.com/p/Bv5O_XxlzZu/

```
