#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
from sys import argv, exit, stderr, stdout
from time import time

from Comment import Comment
from strip_html import strip_ml_tags as stripHtmlTags
from urlopener import urlopener

comments = []
cmntCount = 0
fileName = "comments.txt"
fileOut = 0


def parseCommentsTotalCount(data):
    """
    return comment count, -1 when fail
    """
    p = re.compile(r"\d+ Reviews")

    for line in data:
        line = line.replace(",", "")
        match = re.search(p, line)
        if match != None:
            getNmbr = match.group().split(" ")
            return int(getNmbr[0])
    return -1

def parsePagesTotal(data):
    """
    Page navigation looks like this:
    ------------------------------------------------------
    |        <Previous  |  1  2  3  |  Next>             |
    ------------------------------------------------------
    or
    ------------------------------------------------------
    |  <Previous  |  1 ... 55 [56] 57 ... 152  |  Next>  |
    ------------------------------------------------------
                                               ^
             Match against this --------------´
    """
    p = re.compile(r"(\d|,)*\d*")

    if data is None or len(data) < 1:
        return -1

    for line in reversed(data):
        if "<span class=\"paging\">" in line:
            i = line.rfind("|")
            j = 0
            tmp = 0
            while i > 1:
                if line[i] is '>':
                    j += 1
                    if j is 2:
                        tmp = line[i + 1 : line.rfind("|")] # Format now: 3</a>
                        tmp = re.search(p, tmp)
                        if tmp is not None:
                            tmp = tmp.group(0)
                        else:
                            tmp = 0
                        break
                i -= 1
            link = line.split("\"")
            link = link[len(link) - 2]
            return (int(tmp), link)
    return -1

def generatePageNumberLink(link, pagenumber):
    p = re.compile("pageNumber=\d+")
    return re.sub(p, "pageNumber=%d" % pagenumber, link)

def commentsStartStopLineNmbr(data):
    """
    return (begin, end) tuple which contains linenumbers of start/stop of
    comment area.
    """
    begin = 0
    end = 0
    i = 0

    if data is None or len(data) < 1:
        return None

    while i < len(data):
        if "<table class=\"CMheadingBar\"" in data[i]:
            if begin is 0:
                begin = i
            else:
                end = i
                break
        i += 1
    return (int(begin), int(end))

def parseComments(data):
    """
    Parse comments from site
    """
    n = 1
    reviewBegins = '<div style="margin-left:0.5em;">'
    reviewEnds = '<div style="padding-top: 10px; clear: both; width: 100%;">'
    stars_line = 'margin-right:5px;'
    stars = re.compile('\d+.\d+ out of 5 stars')
    header_line = '<span style="vertical-align:middle;"'
    helpful_line ='people found the following review helpful'
    helpful = re.compile('\d+ of \d+ people found the following review helpful')
    reviewText = '<span class="h3color tiny">' # Actual review

    boundaries = commentsStartStopLineNmbr(data)
    for i in range(boundaries[0], boundaries[1] + 1):
        if reviewBegins in data[i]:
            curcomment = Comment()
            curcomment.number = n
            n += 1
            while reviewEnds not in data[i]:
                # Parse stars
                if stars_line in data[i]:
                    stars_found = re.search(stars, data[i])
                    if stars_found != None:
                        curcomment.stars = stars_found.group()
                # Parse header
                elif header_line in data[i]:
                    line = data[i]
                    begin = line.find('<b>') + 3
                    end = line.find('</b>')
                    curcomment.header = line[begin : end]
                # Parse helpfulness
                elif helpful_line in data[i]:
                    helpful_found = data[i].replace(",", "")
                    helpful_found = re.search(helpful, helpful_found)
                    if helpful_found != None:
                        curcomment.helpful = helpful_found.group()
                # Parse body text
                elif reviewText in data[i]:
                    i += 3
                    data[i] = stripHtmlTags(data[i])
                    curcomment.comment = re.sub("\s+", " ", data[i])
                i += 1
            print curcomment.__repr__()

def cleanUpComment(c):
    """
    return cleaned up comment, '' if fail.
    """
    p = re.compile(r"\s+")
    r = 0

    if c is None or len(c) < 1:
        return ''

    # Thanks Amazon for the nice mark up -> CLEAN IT UP!
    while r < len(c):
        # Multiple spaces to a single space
        if re.search(p, c[r]) != None:
            c[r] = re.sub(p, " ", c[r])
            if re.search(r"^\s", c[r]) != None or c[r] is '':
                c.pop(r)
                continue
        if c[r] is "" or re.search(r"^\n", c[r]) != None:
            c.pop(r)
            continue
        if "---" in c[r]:
            c.pop(r)
            continue
        # FIXME -*- please use tag matcher instead of this glue
        if re.search(r"^\(REAL NAME\)", c[r]) != None:
            c[r] = re.sub(r"^\(REAL NAME\)", "", c[r])
            continue
        r += 1
    return c

def estimatedTimeOfArrival(t, pagesProcessed, pageCount):
    timePassed = time() - t

    if pagesProcessed is 0:
        return 0
    avg = timePassed/pagesProcessed
    return (int(pageCount) - int(pagesProcessed)) * avg

def generatePageLinks(link, pagesTotal):
    """
    Generate a list of comment page links that can be feed for QueueWorker
    """
    return [generatePageNumberLink(link, cnt) for cnt in range(1, pagesTotal + 1)]


# Main function that binds everything together
def main():
    cboundaries = [] # Comment boundaries
    cmntTotal = pageTotal = revStarts = 0
    global cmntCount, comments, fileName, fileOut
    pageCount = 1

    if len(argv) == 1:
        amazonurl = str(raw_input('> '))
    if len(argv) == 2:
        amazonurl = argv[1]
    elif len(argv) >= 3:
        amazonurl = argv[1]
        fileName = argv[2]

    # Don't show that silly banner, we are not going to use it anyway
    if '&showViewpoints=1' in amazonurl:
        amazonurl = amazonurl.replace("&showViewpoints=1", "&showViewpoints=0")

    data = urlopener(amazonurl) # Read data
    if data is None:
        print "Zero data"
        exit(1)

    commentcount = parseCommentsTotalCount(data)
    if commentcount < 1:
        print "No customer reviews available"
        print "(or ugly malfunction)"
        exit(1)

    totalcommPages = parsePagesTotal(data) # returns (pagecount, lastpageurl)
    linklist = generatePageLinks(totalcommPages[1], totalcommPages[0])
    first = urlopener(linklist[0])
    parseComments(first)

    return 0

if __name__ == "__main__":
    main()

