#Vincent Zhang
#Assignment 2
#CIS 400

import twitter
import sys
import time
from urllib2 import URLError
from httplib import BadStatusLine
import json
from functools import partial
from sys import maxint
import networkx as nx
import matplotlib.pyplot as plt


def oauth_login():
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://dev.twitter.com/docs/auth/oauth for more information
    # on Twitter's OAuth implementation.


    # Use your own credentials.
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    OAUTH_TOKEN = ''
    OAUTH_TOKEN_SECRET = ''
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

# Sample usage
twitter_api = oauth_login()

###################################################################################################
#Copied From Cook Book
###################################################################################################
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
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
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
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

##########################################################################################################
#Copied From Cook Book
#########################################################################################################

def get_friends_followers_ids(twitter_api, screen_name=None, user_id=None,
                              friends_limit=maxint, followers_limit=maxint):

    # Must have either screen_name or user_id (logical xor)
    assert (screen_name != None) != (user_id != None),     "Must have screen_name or user_id, but not both"

    # See https://dev.twitter.com/docs/api/1.1/get/friends/ids and
    # https://dev.twitter.com/docs/api/1.1/get/followers/ids for details
    # on API parameters

    get_friends_ids = partial(make_twitter_request, twitter_api.friends.ids,count=5000)
    get_followers_ids = partial(make_twitter_request, twitter_api.followers.ids,count=5000)

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

            #print >> sys.stderr, 'Fetched {0} total {1} ids for {2}'.format(len(ids),
            #                                        label, (user_id or screen_name))

            # XXX: You may want to store data during each iteration to provide an
            # an additional layer of protection from exceptional circumstances

            if len(ids) >= limit or response is None:
                break

    # Do something useful with the IDs, like store them to disk...
    return friends_ids[:friends_limit], followers_ids[:followers_limit]


#######################################################################################
#This part is for testing Step 2 and Step 3. Uncomment to use.


#friends_ids, followers_ids = get_friends_followers_ids(twitter_api,
#                                                       screen_name="RobbyForYaMommy",
#                                                       friends_limit=300,
#                                                       followers_limit=300)


#print "Friends: \n", friends_ids, "\n"
#print "Followers: \n", followers_ids, "\n"
#reciprocal_friends = set(friends_ids) & set(followers_ids)
#print"Printing Reciprocal Friends: \n", reciprocal_friends, "\n"
#######################################################################################


#######################################################################################
#Copied From Cook Book
#######################################################################################

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




###############################################################################################
#Created this function myself
###############################################################################################

def get_popular_reciprocal_friends(twitter_api, user_id):
    id = user_id
    friends_ids, followers_ids = get_friends_followers_ids(twitter_api,
                                                           user_id = id,
                                                           friends_limit=300,
                                                           followers_limit=300)
    """
    Taking the intersection of friends and followers will yield reciprocal friends
    which are the people you follow that also follows you back. Each reciprocal friend's
    profile will be stored in profile_dict. rf_dict will store a dictionary of the reciprocal
    friend's id and their follower count.
    """
    profile_dict = {}
    rf_dict = {}
    top_5_dict = {}
    top_5_list = []
    for x in (set(friends_ids) & set(followers_ids)):
        json_data = json.dumps(get_user_profile(twitter_api, user_ids=[x]), indent = 1)
        profile_dict = json.loads(json_data)
        rf_dict[str(x)] = (profile_dict[str(x)]['followers_count'])
    #print "Reciprocal Friends and Follower Counts: \n",rf_dict, "\n"


    #If state in case the person has less than 5 reciprocal friends, then it will just be
    #however many reciprocal friends he has or the length of rf_dict.

    length = 0
    if len(rf_dict) < 5:
        length = len(rf_dict)
    else:
        length = 5

    #Iterate through the reciprocal friends dictionary(rf_dict)
    #Take the id of the user that has the highest following count and store it in top_5_list
    #I also made a dictionary for the top 5 most popular in case we want to see their id AND follower count
    #Return top_5_list for the most popular reciprocal friends.
    for _ in range(length):
        key_max = max(rf_dict.keys(), key=(lambda k: rf_dict[k]))
        top_5_dict[key_max] = rf_dict[key_max]
        top_5_list.append(int(key_max))
        del rf_dict[key_max]

    return top_5_list
    #return top_5_dict

#Uncomment this print statement to test for getting the 5 most popular friends. You can comment out
#the current return statement and uncomment the commented one to get a dictionary with the followers count
#if you prefer or it is just returning a list of the top 5 most popular reciprocal friends.
#print get_popular_reciprocal_friends(twitter_api, "704203930")



# This is a simplified version of the crawler from blackboard which I modified quite a bit
# It will crawl and get the reciprocal friends using the function I made above.
# I have the BFS Heirarchy structured as a list of dictionaries where the key is the parent node.
# And the value contains a list of the children nodes (a.k.a the 5 most popular reciprocal friend of that user)

user_id = "704203930"
bfs_list = []
response = get_popular_reciprocal_friends(twitter_api, user_id)
ids = next_queue = response

#I have test print statements for printing the ID and it's list of children
#so that I can compare them when I print the BFS heirarchy later to check that it's correct
level = 1
max_level = 3
while level < max_level:
    level += 1
    (queue, next_queue) = (next_queue, [])
    for id in queue:
        bfs_dict2 = {}
        print "id: ", id
        response = get_popular_reciprocal_friends(twitter_api, user_id = id)
        next_queue += response
        print "Children: ", response,"\n"
        bfs_dict2[id] = response
        bfs_list.append(bfs_dict2)

    ids += next_queue
#print ids
bfs_dict = {}
response = get_popular_reciprocal_friends(twitter_api, user_id)
bfs_dict[user_id] = response
bfs_list.insert(0, bfs_dict)

#This will show the BFS Heriarchy
print "Printing BFS List Heirarchy: \n"
for x in bfs_list:
    print x,"\n"

#Creating my graph, make parent node and then make an edge from the parent node to it's children nodes
#if an edge doesn't already exist, hence the if statement to check.
G = nx.MultiGraph()
for item in bfs_list:
    for parent, child_list in item.iteritems():
        G.add_node(parent)
        for child in child_list:
            if (G.has_edge(parent,child) == False):
                G.add_edge(parent,child)

#Printing the proper output
print "Number of Nodes in the graph: ", G.number_of_nodes()
print "Number of Edges in the graph: ", G.number_of_edges()
print "Diameter of the graph: ", nx.diameter(G)
print "Average Distance: ", nx.average_shortest_path_length(G)
nx.draw(G, with_labels = True)
plt.savefig("simple_path.png") # save as png
plt.show() # display

