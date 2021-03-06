import logging
import re

from resources.save import Save

from resources.handlers.tenor import Tenor
from resources.handlers.giphy import Giphy
from resources.handlers.imgur import Imgur
from resources.handlers.redgifs import Redgifs
from resources.handlers.gfycat import Gfycat
from resources.handlers.youtube import YouTube
from resources.handlers.common import Common
from resources.handlers.redditgallery import RedditGallery
from resources.handlers.reddithandler import RedditHandler


def formatName(title):
    '''Removes special characters and shortens long filenames'''
    title = re.sub('[?/|\\:<>*"]', '', title)
    if len(title) > 211:
        title = title[:210]
    return title


def routeSubmission(submission):
    logger = logging.getLogger(__name__)
    save = Save()

    title = formatName(submission.title)
    link = submission.url
    downloaded = True
    path = {
        'author': str(submission.author),
        'subreddit': str(submission.subreddit),
        'id': str(submission.id),
        'created_utc': str(submission.created_utc),
        'title': title,
        'ext': 'txt'
    }

    # Selftext post
    if submission.is_self:
        with open(save.get_dir(path), 'a+') as f:
            f.write(str(submission.selftext.encode('utf-8')))

    # Link to a jpg, png, gifv, gif, jpeg
    elif re.match(Common.valid_url, link):
        if not Common(link, '{}-{}'.format(str(submission.id), title), path).save():
            downloaded = False

    # Imgur
    elif re.match(Imgur.valid_url, link):
        if not Imgur(link, title, path).save():
            downloaded = False

    # Giphy
    elif re.match(Giphy.valid_url, link):
        if not Giphy(link, title, path).save():
            downloaded = False

    # Tenor
    elif re.match(Tenor.valid_url, link):
        if not Tenor(link, title, path).save():
            downloaded = False

    # Redgifs
    elif re.match(Redgifs.valid_url, link):
        if not Redgifs(link, title, path).save():
            downloaded = False

    # Gfycat
    elif re.match(Gfycat.valid_url, link):
        if not Gfycat(link, title, path).save():
            downloaded = False

    elif re.match(RedditGallery.valid_url, link):
        if not RedditGallery(link, title, path).save():
            downloaded = False
    # Flickr
    elif 'flickr.com/' in link:
        downloaded = False
        logger.info("No mathces: No Flickr support {}".format(link))

    # Reddit submission
    elif re.match(RedditHandler.valid_url, link):
        downloaded = False
        logger.debug("Fetching crosspost {}".format(link))
        new_submission = RedditHandler(link, title, path).save()
        if not new_submission:
            downloaded = False
        if not routeSubmission(new_submission):
            downloaded = False

    # youtube_dl supported site
    elif YouTube.yt_supported(link):
        if not YouTube(link, title, path).save():
            downloaded = False

    else:
        logger.info("No matches: {}".format(link))
        downloaded = False

    return downloaded
