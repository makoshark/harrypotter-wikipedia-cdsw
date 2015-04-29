#!/usr/bin/env python
# coding=utf-8

import requests

# get_article_revisions is a function that takes an article title in
# wikipedia and return a list of all the revisions and meatadata for
# that article
def get_article_revisions(title):
    revisions = []

    # create a base url for the api and then a normal url which is initially just a copy of it
    # http://en.wikipedia.org/w/api.php/?action=query&titles=%(article_title)s&prop=revisions&rvprop=flags|timestamp|user|size|ids&rvlimit=500&format=json
    wp_api_url = "http://en.wikipedia.org/w/api.php/"

    parameters = {'action' : 'query',
                  'titles' : title,
                  'prop' : 'revisions',
                  'rvprop' : 'flags|timestamp|user|size|ids',
                  'rvlimit' : 500,
                  'format' : 'json',
                  'continue' : '' }

    # we'll repeat this forever (i.e., we'll only stop when we find
    # the "break" command)
    while True:
        # the first line open the urls but also handles unicode urls
        call = requests.get(wp_api_url, params=parameters)
        api_answer = call.json()

        # get the list of pages from the json object
        pages = api_answer["query"]["pages"]

        # for every pages (there should always be only one) get the revisions
        for page in pages.keys():
            query_revisions = pages[page]["revisions"]

            # for every revision, we do first do cleaning up
            for rev in query_revisions:
                # lets continue/skip if the user is hidden
                if "userhidden" in rev:
                    continue
                
                # 1: add a title field for the article because we're going to mix them together
                rev["title"] = title

                # 2: lets "recode" anon so it's true or false instead of present/missing
                if "anon" in rev:
                    rev["anon"] = True
                else:
                    rev["anon"] = False

                # 3: letst recode "minor" in the same way
                if "minor" in rev:
                    rev["minor"] = True
                else:
                    rev["minor"] = False

                # we're going to change the timestamp to make it work a little better in excel and similar
                rev["timestamp"] = rev["timestamp"].replace("T", " ")
                rev["timestamp"] = rev["timestamp"].replace("Z", "")

                # finally save the revisions we've seen to a varaible
                revisions.append(rev)

        if 'continue' in api_answer:
            parameters.update(api_answer['continue'])
        else:
            break

    # return all the revisions for this page
    return(revisions)

category = "Harry Potter"

# we'll use another api called catscan2 to grab a list of pages in
# categories and subcategories. it works like all the other apis we've
# studied!
#
# http://tools.wmflabs.org/catscan2/catscan2.php?depth=10&categories=%s&doit=1&format=json
url_catscan = "http://tools.wmflabs.org/catscan2/catscan2.php"

parameters = {'depth' : 10,
              'categories' : category,
              'format' : 'json',
              'doit' : 1}

r = requests.get(url_catscan, params=parameters)
articles_json = r.json()
articles = articles_json["*"][0]["a"]["*"]

# open a filie to write all the output
output = open("hp_wiki.tsv", "w", encoding="utf-8")
output.write("\t".join(["title", "user", "timestamp", "size", "anon", "minor", "revid"]) + "\n")

# for every article
for article in articles:

    # first grab tht title
    title = article["a"]["title"]

    # get the list of revisions from our function and then interating through it printinig it out
    revisions = get_article_revisions(title)
    for rev in revisions:
        output.write("\t".join(['"' + rev["title"] + '"', '"' + rev["user"] + '"',
                               rev["timestamp"], str(rev["size"]), str(rev["anon"]),
                               str(rev["minor"]), str(rev["revid"])]) + "\n")

# close the file, we're done here!
output.close()
    
    
