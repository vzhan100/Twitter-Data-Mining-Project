
# coding: utf-8

# #Mining the Social Web, 2nd Edition
#
# ##Chapter 9: Twitter Cookbook
#
# This IPython Notebook provides an interactive way to follow along with and explore the numbered examples from [_Mining the Social Web (2nd Edition)_](http://bit.ly/135dHfs). The intent behind this notebook is to reinforce the concepts from the sample code in a fun, convenient, and effective way. This notebook assumes that you are reading along with the book and have the context of the discussion as you work through these exercises.
#
# In the somewhat unlikely event that you've somehow stumbled across this notebook outside of its context on GitHub, [you can find the full source code repository here](http://bit.ly/16kGNyb).
#
# ## Copyright and Licensing
#
# You are free to use or adapt this notebook for any purpose you'd like. However, please respect the [Simplified BSD License](https://github.com/ptwobrussell/Mining-the-Social-Web-2nd-Edition/blob/master/LICENSE.txt) that governs its use.
#
# ## Notes
#
# This notebook is still a work in progress and currently features 25 recipes. The example titles should be fairly self-explanatory, and the code is designed to be reused as you progress further in the notebook --- meaning that you should follow along and execute each cell along the way since later cells may depend on functions being defined from earlier cells. Consider this notebook draft material at this point.

### Example 1. Accessing Twitter's API for development purposes

# In[ ]:

"""""""""
def oauth_login():
    CONSUMER_KEY = 'TqBkZcqCpyaBrl7waCooq0wq4'
    CONSUMER_SECRET = 'rgaTAiozmnTkODjStb8QFUnUYXzyvUepAv2pbNEArYjqgUQySg'
    OAUTH_TOKEN = '3338276956-p6R1hz04pMLzauza0DX9rRotFiVxIRrJEMNZwBT'
    OAUTH_TOKEN_SECRET = '1tzR6qnMW86p3NhuITZHoWTNPjTRIcyT0x80GbIyPREcG'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

twitter_api = oauth_login()

"""

"""
def oauth_login():
    CONSUMER_KEY = 'HFuGWiCoxAefQUIznGadxjXXr'
    CONSUMER_SECRET = 'KatEUs4IbJQhtmCIqbXB5caZwa5UwVXTUIMOXwZ7yzNkm1lAR0'
    OAUTH_TOKEN = '969723355283763201-31yxDXmISYWb4acq632Txvj5vBUwIwv'
    OAUTH_TOKEN_SECRET = 'guHihhrQxXayPoZ6R1j3t8N5YAtuRY8fEJN27LyKPyb4W'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

twitter_api = oauth_login()
"""



import twitter

def oauth_login():
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://dev.twitter.com/docs/auth/oauth for more information
    # on Twitter's OAuth implementation.

    CONSUMER_KEY = 'Qf2R63mlJSGaekO4vlWTbga7x'
    CONSUMER_SECRET = 'IRx2u7j9IGookrN7O2uW3j1DYam3e3qKpcDP0tLuvqBLngtyWx'
    OAUTH_TOKEN = '969668707999014915-HJtiGm9N6S4zTUiuCPdOSrfQArpgiaR'
    OAUTH_TOKEN_SECRET = 'TPEJc197UzABGoOfHfvntc6p3w08oCw8nDJQGJSpeu2aq'
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

# Sample usage
twitter_api = oauth_login()

# Nothing to see by displaying twitter_api except that it's now a
# defined variable

print twitter_api


### Example 2. Doing the OAuth dance to access Twitter's API for production purposes

# In[ ]:

"""
import json
from flask import Flask, request
import multiprocessing
from threading import Timer
from IPython.display import IFrame
from IPython.display import display
from IPython.display import Javascript as JS

import twitter
from twitter.oauth_dance import parse_oauth_tokens
from twitter.oauth import read_token_file, write_token_file

# Note: This code is exactly the flow presented in the _AppendixB notebook

OAUTH_FILE = "resources/ch09-twittercookbook/twitter_oauth"

# XXX: Go to http://twitter.com/apps/new to create an app and get values
# for these credentials that you'll need to provide in place of these
# empty string values that are defined as placeholders.
# See https://dev.twitter.com/docs/auth/oauth for more information
# on Twitter's OAuth implementation, and ensure that *oauth_callback*
# is defined in your application settings as shown next if you are
# using Flask in this IPython Notebook.

# Define a few variables that will bleed into the lexical scope of a couple of
# functions that follow
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
oauth_callback = 'http://127.0.0.1:5000/oauth_helper'

# Set up a callback handler for when Twitter redirects back to us after the user
# authorizes the app

webserver = Flask("TwitterOAuth")
@webserver.route("/oauth_helper")
def oauth_helper():

    oauth_verifier = request.args.get('oauth_verifier')

    # Pick back up credentials from ipynb_oauth_dance
    oauth_token, oauth_token_secret = read_token_file(OAUTH_FILE)

    _twitter = twitter.Twitter(
        auth=twitter.OAuth(
            oauth_token, oauth_token_secret, CONSUMER_KEY, CONSUMER_SECRET),
        format='', api_version=None)

    oauth_token, oauth_token_secret = parse_oauth_tokens(
        _twitter.oauth.access_token(oauth_verifier=oauth_verifier))

    # This web server only needs to service one request, so shut it down
    shutdown_after_request = request.environ.get('werkzeug.server.shutdown')
    shutdown_after_request()

    # Write out the final credentials that can be picked up after the following
    # blocking call to webserver.run().
    write_token_file(OAUTH_FILE, oauth_token, oauth_token_secret)
    return "%s %s written to %s" % (oauth_token, oauth_token_secret, OAUTH_FILE)

# To handle Twitter's OAuth 1.0a implementation, we'll just need to implement a
# custom "oauth dance" and will closely follow the pattern defined in
# twitter.oauth_dance.

def ipynb_oauth_dance():

    _twitter = twitter.Twitter(
        auth=twitter.OAuth('', '', CONSUMER_KEY, CONSUMER_SECRET),
        format='', api_version=None)

    oauth_token, oauth_token_secret = parse_oauth_tokens(
            _twitter.oauth.request_token(oauth_callback=oauth_callback))

    # Need to write these interim values out to a file to pick up on the callback
    # from Twitter that is handled by the web server in /oauth_helper
    write_token_file(OAUTH_FILE, oauth_token, oauth_token_secret)

    oauth_url = ('http://api.twitter.com/oauth/authorize?oauth_token=' + oauth_token)

    # Tap the browser's native capabilities to access the web server through a new
    # window to get user authorization
    display(JS("window.open('%s')" % oauth_url))

# After the webserver.run() blocking call, start the OAuth Dance that will
# ultimately cause Twitter to redirect a request back to it. Once that request
# is serviced, the web server will shut down and program flow will resume
# with the OAUTH_FILE containing the necessary credentials.
Timer(1, lambda: ipynb_oauth_dance()).start()

webserver.run(host='0.0.0.0')

# The values that are read from this file are written out at
# the end of /oauth_helper
oauth_token, oauth_token_secret = read_token_file(OAUTH_FILE)

# These four credentials are what is needed to authorize the application
auth = twitter.oauth.OAuth(oauth_token, oauth_token_secret,
                               CONSUMER_KEY, CONSUMER_SECRET)

twitter_api = twitter.Twitter(auth=auth)

print twitter_api
"""


### Example 3. Discovering the trending topics

# In[ ]:

import json
import twitter

def twitter_trends(twitter_api, woe_id):
    # Prefix ID with the underscore for query string parameterization.
    # Without the underscore, the twitter package appends the ID value
    # to the URL itself as a special-case keyword argument.
    return twitter_api.trends.place(_id=woe_id)

# Sample usage

twitter_api = oauth_login()

# See https://dev.twitter.com/docs/api/1.1/get/trends/place and
# http://developer.yahoo.com/geo/geoplanet/ for details on
# Yahoo! Where On Earth ID

WORLD_WOE_ID = 1
world_trends = twitter_trends(twitter_api, WORLD_WOE_ID)
print json.dumps(world_trends, indent=1)

US_WOE_ID = 23424977
us_trends = twitter_trends(twitter_api, US_WOE_ID)
print json.dumps(us_trends, indent=1)


### Example 4. Searching for tweets

# In[ ]:

def twitter_search(twitter_api, q, max_results=200, **kw):

    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets and
    # https://dev.twitter.com/docs/using-search for details on advanced
    # search criteria that may be useful for keyword arguments

    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)

    statuses = search_results['statuses']

    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://dev.twitter.com/docs/rate-limiting/1.1/limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.

    # Enforce a reasonable limit
    max_results = min(1000, max_results)

    for _ in range(10): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break

        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=')
                        for kv in next_results[1:].split("&") ])

        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']

        if len(statuses) > max_results:
            break

    return statuses

# Sample usage

twitter_api = oauth_login()

q = "CrossFit"
results = twitter_search(twitter_api, q, max_results=10)

# Show one sample search result by slicing the list...
print json.dumps(results[0], indent=1)


### Example 5. Constructing convenient function calls

# In[ ]:

from functools import partial

pp = partial(json.dumps, indent=1)

twitter_world_trends = partial(twitter_trends, twitter_api, WORLD_WOE_ID)

print pp(twitter_world_trends())

authenticated_twitter_search = partial(twitter_search, twitter_api)
results = authenticated_twitter_search("iPhone")
print pp(results)

authenticated_iphone_twitter_search = partial(authenticated_twitter_search, "iPhone")
results = authenticated_iphone_twitter_search()
print pp(results)


### Example 6. Saving and restoring JSON data with flat-text files

# In[ ]:

import io, json

def save_json(filename, data):
    with io.open('resources/ch09-twittercookbook/{0}.json'.format(filename),
                 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))

def load_json(filename):
    with io.open('resources/ch09-twittercookbook/{0}.json'.format(filename),
                 encoding='utf-8') as f:
        return f.read()

# Sample usage

q = 'CrossFit'

twitter_api = oauth_login()
results = twitter_search(twitter_api, q, max_results=10)

save_json(q, results)
results = load_json(q)

print json.dumps(results, indent=1)


### Example 7. Saving and accessing JSON data with MongoDB

# In[ ]:

import json
import pymongo # pip install pymongo

def save_to_mongo(data, mongo_db, mongo_db_coll, **mongo_conn_kw):

    # Connects to the MongoDB server running on
    # localhost:27017 by default

    client = pymongo.MongoClient(**mongo_conn_kw)

    # Get a reference to a particular database

    db = client[mongo_db]

    # Reference a particular collection in the database

    coll = db[mongo_db_coll]

    # Perform a bulk insert and  return the IDs

    return coll.insert(data)

def load_from_mongo(mongo_db, mongo_db_coll, return_cursor=False,
                    criteria=None, projection=None, **mongo_conn_kw):

    # Optionally, use criteria and projection to limit the data that is
    # returned as documented in
    # http://docs.mongodb.org/manual/reference/method/db.collection.find/

    # Consider leveraging MongoDB's aggregations framework for more
    # sophisticated queries.

    client = pymongo.MongoClient(**mongo_conn_kw)
    db = client[mongo_db]
    coll = db[mongo_db_coll]

    if criteria is None:
        criteria = {}

    if projection is None:
        cursor = coll.find(criteria)
    else:
        cursor = coll.find(criteria, projection)

    # Returning a cursor is recommended for large amounts of data

    if return_cursor:
        return cursor
    else:
        return [ item for item in cursor ]

# Sample usage

q = 'CrossFit'

twitter_api = oauth_login()
results = twitter_search(twitter_api, q, max_results=10)

save_to_mongo(results, 'search_results', q)

load_from_mongo('search_results', q)


### Example 8. Sampling the Twitter firehose with the Streaming API

# In[ ]:

# Finding topics of interest by using the filtering capablities it offers.

import sys
import twitter

# Query terms

q = 'CrossFit' # Comma-separated list of terms

print >> sys.stderr, 'Filtering the public timeline for track="%s"' % (q,)
sys.stderr.flush()

# Returns an instance of twitter.Twitter
twitter_api = oauth_login()

# Reference the self.auth parameter
twitter_stream = twitter.TwitterStream(auth=twitter_api.auth)

# See https://dev.twitter.com/docs/streaming-apis
stream = twitter_stream.statuses.filter(track=q)

# For illustrative purposes, when all else fails, search for Justin Bieber
# and something is sure to turn up (at least, on Twitter)

for tweet in stream:
    print tweet['text']
    sys.stdout.flush()

    # Save to a database in a particular collection


### Example 9. Collecting time-series data

# In[ ]:

import sys
import datetime
import time
import twitter

def get_time_series_data(api_func, mongo_db_name, mongo_db_coll,
                         secs_per_interval=60, max_intervals=15, **mongo_conn_kw):

    # Default settings of 15 intervals and 1 API call per interval ensure that
    # you will not exceed the Twitter rate limit.

    interval = 0

    while True:

        # A timestamp of the form "2013-06-14 12:52:07"
        now = str(datetime.datetime.now()).split(".")[0]

        ids = save_to_mongo(api_func(), mongo_db_name, mongo_db_coll + "-" + now)

        print >> sys.stderr, "Write {0} trends".format(len(ids))
        print >> sys.stderr, "Zzz..."
        print >> sys.stderr.flush()

        time.sleep(secs_per_interval) # seconds
        interval += 1

        if interval >= 15:
            break

# Sample usage

get_time_series_data(twitter_world_trends, 'time-series', 'twitter_world_trends')


### Example 10. Extracting tweet entities

# In[ ]:

def extract_tweet_entities(statuses):

    # See https://dev.twitter.com/docs/tweet-entities for more details on tweet
    # entities

    if len(statuses) == 0:
        return [], [], [], [], []

    screen_names = [ user_mention['screen_name']
                         for status in statuses
                            for user_mention in status['entities']['user_mentions'] ]

    hashtags = [ hashtag['text']
                     for status in statuses
                        for hashtag in status['entities']['hashtags'] ]

    urls = [ url['expanded_url']
                     for status in statuses
                        for url in status['entities']['urls'] ]

    symbols = [ symbol['text']
                   for status in statuses
                       for symbol in status['entities']['symbols'] ]

    # In some circumstances (such as search results), the media entity
    # may not appear
    if status['entities'].has_key('media'):
        media = [ media['url']
                         for status in statuses
                            for media in status['entities']['media'] ]
    else:
        media = []

    return screen_names, hashtags, urls, media, symbols

# Sample usage

q = 'CrossFit'

statuses = twitter_search(twitter_api, q)

screen_names, hashtags, urls, media, symbols = extract_tweet_entities(statuses)

# Explore the first five items for each...

print json.dumps(screen_names[0:5], indent=1)
print json.dumps(hashtags[0:5], indent=1)
print json.dumps(urls[0:5], indent=1)
print json.dumps(media[0:5], indent=1)
print json.dumps(symbols[0:5], indent=1)


### Example 11. Finding the most popular tweets in a collection of tweets

# In[ ]:

import twitter

def find_popular_tweets(twitter_api, statuses, retweet_threshold=3):

    # You could also consider using the favorite_count parameter as part of
    # this  heuristic, possibly using it to provide an additional boost to
    # popular tweets in a ranked formulation

    return [ status
                for status in statuses
                    if status['retweet_count'] > retweet_threshold ]

# Sample usage

q = "CrossFit"

twitter_api = oauth_login()
search_results = twitter_search(twitter_api, q, max_results=200)

popular_tweets = find_popular_tweets(twitter_api, search_results)

for tweet in popular_tweets:
    print tweet['text'], tweet['retweet_count']


### Example 12. Finding the most popular tweet entities in a collection of tweets

# In[ ]:

import twitter
from collections import Counter

def get_common_tweet_entities(statuses, entity_threshold=3):

    # Create a flat list of all tweet entities
    tweet_entities = [  e
                        for status in statuses
                            for entity_type in extract_tweet_entities([status])
                                for e in entity_type
                     ]

    c = Counter(tweet_entities).most_common()

    # Compute frequencies
    return [ (k,v)
             for (k,v) in c
                 if v >= entity_threshold
           ]

# Sample usage

q = 'CrossFit'

twitter_api = oauth_login()
search_results = twitter_search(twitter_api, q, max_results=100)
common_entities = get_common_tweet_entities(search_results)

print "Most common tweet entities"
print common_entities


### Example 13. Tabulating frequency analysis

# In[ ]:

from prettytable import PrettyTable

# Get some frequency data

twitter_api = oauth_login()
search_results = twitter_search(twitter_api, q, max_results=100)
common_entities = get_common_tweet_entities(search_results)

# Use PrettyTable to create a nice tabular display

pt = PrettyTable(field_names=['Entity', 'Count'])
[ pt.add_row(kv) for kv in common_entities ]
pt.align['Entity'], pt.align['Count'] = 'l', 'r' # Set column alignment
print pt


### Example 14. Finding users who have retweeted a status

# In[ ]:

import twitter

twitter_api = oauth_login()

print """User IDs for retweeters of a tweet by @fperez_org
that was retweeted by @SocialWebMining and that @jyeee then retweeted
from @SocialWebMining's timeline\n"""
print twitter_api.statuses.retweeters.ids(_id=334188056905129984)['ids']
print json.dumps(twitter_api.statuses.show(_id=334188056905129984), indent=1)
print

print "@SocialWeb's retweet of @fperez_org's tweet\n"
print twitter_api.statuses.retweeters.ids(_id=345723917798866944)['ids']
print json.dumps(twitter_api.statuses.show(_id=345723917798866944), indent=1)
print

print "@jyeee's retweet of @fperez_org's tweet\n"
print twitter_api.statuses.retweeters.ids(_id=338835939172417537)['ids']
print json.dumps(twitter_api.statuses.show(_id=338835939172417537), indent=1)


### Example 15. Extracting a retweet's attribution

# In[ ]:

import re

def get_rt_attributions(tweet):

    # Regex adapted from Stack Overflow (http://bit.ly/1821y0J)

    rt_patterns = re.compile(r"(RT|via)((?:\b\W*@\w+)+)", re.IGNORECASE)
    rt_attributions = []

    # Inspect the tweet to see if it was produced with /statuses/retweet/:id.
    # See https://dev.twitter.com/docs/api/1.1/get/statuses/retweets/%3Aid.

    if tweet.has_key('retweeted_status'):
        attribution = tweet['retweeted_status']['user']['screen_name'].lower()
        rt_attributions.append(attribution)

    # Also, inspect the tweet for the presence of "legacy" retweet patterns
    # such as "RT" and "via", which are still widely used for various reasons
    # and potentially very useful. See https://dev.twitter.com/discussions/2847
    # and https://dev.twitter.com/discussions/1748 for some details on how/why.

    try:
        rt_attributions += [
                        mention.strip()
                        for mention in rt_patterns.findall(tweet['text'])[0][1].split()
                      ]
    except IndexError, e:
        pass

    # Filter out any duplicates

    return list(set([rta.strip("@").lower() for rta in rt_attributions]))

# Sample usage
twitter_api = oauth_login()

tweet = twitter_api.statuses.show(_id=214746575765913602)
print get_rt_attributions(tweet)
print
tweet = twitter_api.statuses.show(_id=345723917798866944)
print get_rt_attributions(tweet)


### Example 16. Making robust Twitter requests

# In[ ]:

import sys
import time
from urllib2 import URLError
from httplib import BadStatusLine
import json
import twitter

def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw):

    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):

        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e

        # See https://dev.twitter.com/docs/error-codes-responses for common codes

        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429:
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' %                 (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function

    wait_period = 2
    error_count = 0

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            time.sleep(wait_period)
            wait_period *= 1.5
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

# Sample usage

twitter_api = oauth_login()

# See https://dev.twitter.com/docs/api/1.1/get/users/lookup for
# twitter_api.users.lookup

response = make_twitter_request(twitter_api.users.lookup,
                                screen_name="SocialWebMining")

print json.dumps(response, indent=1)


### Example 17. Resolving user profile information

# In[ ]:

def get_user_profile(twitter_api, screen_names=None, user_ids=None):

    # Must have either screen_name or user_id (logical xor)
    assert (screen_names != None) != (user_ids != None),     "Must have screen_names or user_ids, but not both"

    items_to_info = {}

    items = screen_names or user_ids

    while len(items) > 0:

        # Process 100 items at a time per the API specifications for /users/lookup.
        # See https://dev.twitter.com/docs/api/1.1/get/users/lookup for details.

        items_str = ','.join([str(item) for item in items[:100]])
        items = items[100:]

        if screen_names:
            response = make_twitter_request(twitter_api.users.lookup,
                                            screen_name=items_str)
        else: # user_ids
            response = make_twitter_request(twitter_api.users.lookup,
                                            user_id=items_str)

        for user_info in response:
            if screen_names:
                items_to_info[user_info['screen_name']] = user_info
            else: # user_ids
                items_to_info[user_info['id']] = user_info

    return items_to_info

# Sample usage

twitter_api = oauth_login()

print get_user_profile(twitter_api, screen_names=["SocialWebMining", "ptwobrussell"])
#print get_user_profile(twitter_api, user_ids=[132373965])


### Example 18. Extracting tweet entities from arbitrary text

# In[ ]:

import twitter_text

# Sample usage

txt = "RT @SocialWebMining Mining 1M+ Tweets About #Syria http://wp.me/p3QiJd-1I"

ex = twitter_text.Extractor(txt)

print "Screen Names:", ex.extract_mentioned_screen_names_with_indices()
print "URLs:", ex.extract_urls_with_indices()
print "Hashtags:", ex.extract_hashtags_with_indices()


### Example 19. Getting all friends or followers for a user

# In[ ]:

from functools import partial
from sys import maxint

def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):

    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None),     "Must have screen_name or user_id, but not both"

    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters

    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids,
                              count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids,
                                count=5000)

    friends_ids, followers_ids = [], []

    for twitter_api_func, limit, ids, label in [
                    [get_friends_ids, friends_limit, friends_ids, "friends"],
                    [get_followers_ids, followers_limit, followers_ids, "followers"]
                ]:

        if limit == 0: continue

        cursor = -1
        while cursor != 0:

            # Use make_twitter_request via the partially bound callable...
            if screen_name:
                response = twitter_api_func(screen_name=screen_name, cursor=cursor)
            else: # user_id
                response = twitter_api_func(user_id=user_id, cursor=cursor)

            if response is not None:
                ids += response['ids']
                cursor = response['next_cursor']

            print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids),
                                                    label, (user_id or screen_name))

            # XXX: You may want to store data during each iteration to provide an
            # an additional layer of protection from exceptional circumstances

            if len(ids) >= limit or response is None:
                break

    # Do something useful with the IDs, like store them to disk...
    return friends_ids[:friends_limit], followers_ids[:followers_limit]

# Sample usage

twitter_api = oauth_login()

friends_ids, followers_ids = get_friends_followers_ids(twitter_api,
                                                       screen_name="SocialWebMining",
                                                       friends_limit=10,
                                                       followers_limit=10)

print friends_ids
print followers_ids


### Example 20. Analyzing a user's friends and followers

# In[ ]:

def setwise_friends_followers_analysis(screen_name, friends_ids, followers_ids):

    friends_ids, followers_ids = set(friends_ids), set(followers_ids)

    print '{0} is following {1}'.format(screen_name, len(friends_ids))

    print '{0} is being followed by {1}'.format(screen_name, len(followers_ids))

    print '{0} of {1} are not following {2} back'.format(
            len(friends_ids.difference(followers_ids)),
            len(friends_ids), screen_name)

    print '{0} of {1} are not being followed back by {2}'.format(
            len(followers_ids.difference(friends_ids)),
            len(followers_ids), screen_name)

    print '{0} has {1} mutual friends'.format(
            screen_name, len(friends_ids.intersection(followers_ids)))

# Sample usage

screen_name = "ptwobrussell"

twitter_api = oauth_login()

friends_ids, followers_ids = get_friends_followers_ids(twitter_api,
                                                       screen_name=screen_name)
setwise_friends_followers_analysis(screen_name, friends_ids, followers_ids)


### Example 21. Harvesting a user's tweets

# In[ ]:

def harvest_user_timeline(twitter_api, screen_name=None, user_id=None, max_results=1000):

    assert (screen_name != None) != (user_id != None),     "Must have screen_name or user_id, but not both"

    kw = {  # Keyword args for the Twitter API call
        'count': 200,
        'trim_user': 'true',
        'include_rts' : 'true',
        'since_id' : 1
        }

    if screen_name:
        kw['screen_name'] = screen_name
    else:
        kw['user_id'] = user_id

    max_pages = 16
    results = []

    tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)

    if tweets is None: # 401 (Not Authorized) - Need to bail out on loop entry
        tweets = []

    results += tweets

    print >> sys.stderr, 'Fetched %i tweets' % len(tweets)

    page_num = 1

    # Many Twitter accounts have fewer than 200 tweets so you don't want to enter
    # the loop and waste a precious request if max_results = 200.

    # Note: Analogous optimizations could be applied inside the loop to try and
    # save requests. e.g. Don't make a third request if you have 287 tweets out of
    # a possible 400 tweets after your second request. Twitter does do some
    # post-filtering on censored and deleted tweets out of batches of 'count', though,
    # so you can't strictly check for the number of results being 200. You might get
    # back 198, for example, and still have many more tweets to go. If you have the
    # total number of tweets for an account (by GET /users/lookup/), then you could
    # simply use this value as a guide.

    if max_results == kw['count']:
        page_num = max_pages # Prevent loop entry

    while page_num < max_pages and len(tweets) > 0 and len(results) < max_results:

        # Necessary for traversing the timeline in Twitter's v1.1 API:
        # get the next query's max-id parameter to pass in.
        # See https://dev.twitter.com/docs/working-with-timelines.
        kw['max_id'] = min([ tweet['id'] for tweet in tweets]) - 1

        tweets = make_twitter_request(twitter_api.statuses.user_timeline, **kw)
        results += tweets

        print >> sys.stderr, 'Fetched %i tweets' % (len(tweets),)

        page_num += 1

    print >> sys.stderr, 'Done fetching tweets'

    return results[:max_results]

# Sample usage

twitter_api = oauth_login()
tweets = harvest_user_timeline(twitter_api, screen_name="SocialWebMining",                                max_results=200)

# Save to MongoDB with save_to_mongo or a local file with save_json...


### Example 22. Crawling a friendship graph

# In[ ]:

def crawl_followers(twitter_api, screen_name, limit=1000000, depth=2):

    # Resolve the ID for screen_name and start working with IDs for consistency
    # in storage

    seed_id = str(twitter_api.users.show(screen_name=screen_name)['id'])

    _, next_queue = get_friends_followers_ids(twitter_api, user_id=seed_id,
                                              friends_limit=0, followers_limit=limit)

    # Store a seed_id => _follower_ids mapping in MongoDB

    save_to_mongo({'followers' : [ _id for _id in next_queue ]}, 'followers_crawl',
                  '{0}-follower_ids'.format(seed_id))

    d = 1
    while d < depth:
        d += 1
        (queue, next_queue) = (next_queue, [])
        for fid in queue:
            _, follower_ids = get_friends_followers_ids(twitter_api, user_id=fid,
                                                     friends_limit=0,
                                                     followers_limit=limit)

            # Store a fid => follower_ids mapping in MongoDB
            save_to_mongo({'followers' : [ _id for _id in follower_ids ]},
                          'followers_crawl', '{0}-follower_ids'.format(fid))

            next_queue += follower_ids

# Sample usage

screen_name = "timoreilly"

twitter_api = oauth_login()

crawl_followers(twitter_api, screen_name, depth=1, limit=10)


### Example 23. Analyzing tweet content

# In[ ]:

def analyze_tweet_content(statuses):

    if len(statuses) == 0:
        print "No statuses to analyze"
        return

    # A nested helper function for computing lexical diversity
    def lexical_diversity(tokens):
        return 1.0*len(set(tokens))/len(tokens)

    # A nested helper function for computing the average number of words per tweet
    def average_words(statuses):
        total_words = sum([ len(s.split()) for s in statuses ])
        return 1.0*total_words/len(statuses)

    status_texts = [ status['text'] for status in statuses ]
    screen_names, hashtags, urls, media, _ = extract_tweet_entities(statuses)

    # Compute a collection of all words from all tweets
    words = [ w
          for t in status_texts
              for w in t.split() ]

    print "Lexical diversity (words):", lexical_diversity(words)
    print "Lexical diversity (screen names):", lexical_diversity(screen_names)
    print "Lexical diversity (hashtags):", lexical_diversity(hashtags)
    print "Averge words per tweet:", average_words(status_texts)


# Sample usage

q = 'CrossFit'
twitter_api = oauth_login()
search_results = twitter_search(twitter_api, q)

analyze_tweet_content(search_results)


### Example 24. Summarizing link targets

# In[ ]:

import sys
import json
import nltk
import numpy
import requests
from boilerpipe.extract import Extractor

def summarize(url=None, html=None, n=100, cluster_threshold=5, top_sentences=5):

    # Adapted from "The Automatic Creation of Literature Abstracts" by H.P. Luhn
    #
    # Parameters:
    # * n  - Number of words to consider
    # * cluster_threshold - Distance between words to consider
    # * top_sentences - Number of sentences to return for a "top n" summary

    # Begin - nested helper function
    def score_sentences(sentences, important_words):
        scores = []
        sentence_idx = -1

        for s in [nltk.tokenize.word_tokenize(s) for s in sentences]:

            sentence_idx += 1
            word_idx = []

            # For each word in the word list...
            for w in important_words:
                try:
                    # Compute an index for important words in each sentence

                    word_idx.append(s.index(w))
                except ValueError, e: # w not in this particular sentence
                    pass

            word_idx.sort()

            # It is possible that some sentences may not contain any important words
            if len(word_idx)== 0: continue

            # Using the word index, compute clusters with a max distance threshold
            # for any two consecutive words

            clusters = []
            cluster = [word_idx[0]]
            i = 1
            while i < len(word_idx):
                if word_idx[i] - word_idx[i - 1] < cluster_threshold:
                    cluster.append(word_idx[i])
                else:
                    clusters.append(cluster[:])
                    cluster = [word_idx[i]]
                i += 1
            clusters.append(cluster)

            # Score each cluster. The max score for any given cluster is the score
            # for the sentence.

            max_cluster_score = 0
            for c in clusters:
                significant_words_in_cluster = len(c)
                total_words_in_cluster = c[-1] - c[0] + 1
                score = 1.0 * significant_words_in_cluster                     * significant_words_in_cluster / total_words_in_cluster

                if score > max_cluster_score:
                    max_cluster_score = score

            scores.append((sentence_idx, score))

        return scores

    # End - nested helper function

    extractor = Extractor(extractor='ArticleExtractor', url=url, html=html)

    # It's entirely possible that this "clean page" will be a big mess. YMMV.
    # The good news is that the summarize algorithm inherently accounts for handling
    # a lot of this noise.

    txt = extractor.getText()

    sentences = [s for s in nltk.tokenize.sent_tokenize(txt)]
    normalized_sentences = [s.lower() for s in sentences]

    words = [w.lower() for sentence in normalized_sentences for w in
             nltk.tokenize.word_tokenize(sentence)]

    fdist = nltk.FreqDist(words)

    top_n_words = [w[0] for w in fdist.items()
            if w[0] not in nltk.corpus.stopwords.words('english')][:n]

    scored_sentences = score_sentences(normalized_sentences, top_n_words)

    # Summarization Approach 1:
    # Filter out nonsignificant sentences by using the average score plus a
    # fraction of the std dev as a filter

    avg = numpy.mean([s[1] for s in scored_sentences])
    std = numpy.std([s[1] for s in scored_sentences])
    mean_scored = [(sent_idx, score) for (sent_idx, score) in scored_sentences
                   if score > avg + 0.5 * std]

    # Summarization Approach 2:
    # Another approach would be to return only the top N ranked sentences

    top_n_scored = sorted(scored_sentences, key=lambda s: s[1])[-top_sentences:]
    top_n_scored = sorted(top_n_scored, key=lambda s: s[0])

    # Decorate the post object with summaries

    return dict(top_n_summary=[sentences[idx] for (idx, score) in top_n_scored],
                mean_scored_summary=[sentences[idx] for (idx, score) in mean_scored])

# Sample usage

sample_url = 'http://radar.oreilly.com/2013/06/phishing-in-facebooks-pond.html'
summary = summarize(url=sample_url)

# Alternatively, you can pass in HTML if you have it. Sometimes this approach may be
# necessary if you encounter mysterious urllib2.BadStatusLine errors. Here's how
# that would work:

# sample_html = requests.get(sample_url).text
# summary = summarize(html=sample_html)

print "-------------------------------------------------"
print "                'Top N Summary'"
print "-------------------------------------------------"
print " ".join(summary['top_n_summary'])
print
print
print "-------------------------------------------------"
print "             'Mean Scored' Summary"
print "-------------------------------------------------"
print " ".join(summary['mean_scored_summary'])


### Example 25. Analyzing a user's favorite tweets

# In[ ]:


def analyze_favorites(twitter_api, screen_name, entity_threshold=2):

    # Could fetch more than 200 by walking the cursor as shown in other
    # recipes, but 200 is a good sample to work with.
    favs = twitter_api.favorites.list(screen_name=screen_name, count=200)
    print "Number of favorites:", len(favs)

    # Figure out what some of the common entities are, if any, in the content

    common_entities = get_common_tweet_entities(favs,
                                                entity_threshold=entity_threshold)

    # Use PrettyTable to create a nice tabular display

    pt = PrettyTable(field_names=['Entity', 'Count'])
    [ pt.add_row(kv) for kv in common_entities ]
    pt.align['Entity'], pt.align['Count'] = 'l', 'r' # Set column alignment

    print
    print "Common entities in favorites..."
    print pt


    # Print out some other stats
    print
    print "Some statistics about the content of the favorities..."
    print
    analyze_tweet_content(favs)

    # Could also start analyzing link content or summarized link content, and more.

# Sample usage

twitter_api = oauth_login()
analyze_favorites(twitter_api, "ptwobrussell")


# In[ ]:



