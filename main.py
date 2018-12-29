from __future__ import print_function

import sys

import numpy as np
from matplotlib import pyplot as plt

import json

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

# specify access token
ACCESS_TOKEN = ''

def main():

    # defining URLs
    post_url = 'https://api.instagram.com/v1/tags/CapitalOne/media/recent/'
    user_url = 'https://api.instagram.com/v1/users/'
    pos_url = 'http://www.unc.edu/~ncaren/haphazard/positive.txt'
    neg_url = 'http://www.unc.edu/~ncaren/haphazard/negative.txt'

    # get the latest posts for #CapitalOne
    print(post_url + '?access_token=' + ACCESS_TOKEN)
    resp = urlopen(post_url + '?access_token=' + ACCESS_TOKEN)

    # convert json response to python dictionary
    post_data = json.loads(resp.read().decode('utf-8'))

    print(post_data)

    # PROBLEM 1

    # get the like count of for the first 20 posts
    print("Likes for 20 most recent posts of #CapitalOne:")
    for i in range(0, 20):
        likes = post_data['data'][i]['likes']['count']
        print("post " + str(i+1) + " likes: " + str(likes))
    print("")

    # PROBLEM 2

    # for the top 20 posts: find the following about the posters
    # 1. number of posts
    # 2. number followers
    # 3. number following
    print("Info users who posted 20 most recent posts of #CapitalOne:")
    for i in range(0, 20):
        username = post_data['data'][i]['user']['username']
        print(username + ":")
        user_id = post_data['data'][i]['user']['id']

        user_obj = urlopen(user_url + user_id + ACCESS_TOKEN)
        user_data = json.load(user_obj)

        print("\tposts: " + str(user_data['data']['counts']['media'])) # posts
        print("\tfollowed by: " + str(user_data['data']['counts']['followed_by'])) # followed by
        print("\tfollowing: " + str(user_data['data']['counts']['follows'])) # following
        print("")

    # PROBLEM 3

    # find how many of the posts are positive, negative, and neutral towards CapitalOne
    print("Finding out how many of the 20 posts are positive, negative, or neutral towards CapitalOne:")

    # getting list of positive and negative words
    pos_words = urlopen(pos_url).read().split('\n')
    neg_words = urlopen(neg_url).read().split('\n')

    positive, negative, neutral = feeling(post_data, pos_words, neg_words, 20)

    print("number of positive posts: " + str(positive))
    print("number of negative posts: " + str(negative))
    print("number of neutral posts: " + str(neutral))

    # PROBLEM 4

    # getting data for the latest 100 posts
    positive, negative, neutral = feeling(post_data, pos_words, neg_words, 100)

    # printing the data
    print("\nFinding out how many of the 100 posts are positive, negative, or neutral towards CapitalOne:")
    print("number of positive posts: " + str(positive))
    print("number of negative posts: " + str(negative))
    print("number of neutral posts: " + str(neutral))

    # creating the new plot
    fig = plt.figure("#CapitalOne")
    ax = fig.add_subplot(111)

    # setting up the bars
    ind = np.arange(3)
    bar_data = [positive, negative, neutral]
    width = 0.35
    ax.bar(ind, bar_data, width)

    # setting up the x-axis labels
    ax.set_xlim(0 - width, 2 + 2*width)
    ax.set_xlabel('Feeling')
    ax.set_xticks(ind+width/2)
    ax.set_xticklabels(['positive', 'negative', 'neutral'])

    # setting up the y-axis labels
    ax.set_ylim(0, positive + negative + neutral)
    ax.set_ylabel('Number of posts')

    # setting the title
    ax.set_title("Feeling Data of Latest " + str(positive + negative + neutral) + " Posts containing #CapitalOne")

    plt.show()


def feeling(post_data, pos_words, neg_words, count):

    # setting the initial variables
    positive = 0
    negative = 0
    neutral = 0

    while count > 0:

        # get total counts for positive and negative
        pos_sum = 0
        neg_sum = 0

        for caption_data in post_data['data']:
            caption = caption_data['caption']['text']

            # total number of positive words in captions
            for pos_word in pos_words:
                if pos_word in caption:
                    pos_sum += 1

            # total number of negative words in captions
            for neg_word in neg_words:
                if neg_word in caption:
                    neg_sum += 1

        # find average positive and negative words per post
        pos_avg = pos_sum / len(post_data['data'])
        neg_avg = neg_sum / len(post_data['data'])

        # find positivity and negativity of posts
        for caption_data in post_data['data']:
            caption = caption_data['caption']['text']

            pos_feel = 0
            neg_feel = 0

            # number of positive words in post
            for pos_word in pos_words:
                if pos_word in caption:
                    pos_feel += 1

            # number of negative words in post
            for neg_word in neg_words:
                if neg_word in caption:
                    neg_feel += 1

            # determine if positive and/or negative threshold is met
            feels = 0
            if pos_feel > pos_avg:
                feels += 1
            if neg_feel > neg_avg:
                feels -= 1

            # determine from 'feeling' if contents of post are positive or negative
            if feels > 0:
                positive += 1
            elif feels < 0:
                negative += 1
            else:
                neutral += 1

        # get the next group of posts
        next_url = post_data['pagination']['next_url']
        post_data = json.load(urlopen(next_url))

        # decrement count, since each group contains 20 posts
        count -= 20

    return positive, negative, neutral

if __name__ == "__main__":
    main()
