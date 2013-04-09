##!/usr/bin/env python

import tweepy, urllib, urllib2, json, requests, logging

#Twitter tokens
consumer_key = "S5Akv7vW8zQEujW6j67GQ"
consumer_secret = "vReRo7QuRnJNVhGHTUMQjE9CkgDr3WPNYePoOaljeU"
access_key = "350125914-hwlA4CryOjwBUnmkGyTaFThJhIWMqASBzrgFKT12"
access_secret = "8aQcHplCbenVI3WlRB2alIGvbn5LCyfQNhpGHYR6oQ"

#VK tokens
#url for token: https://oauth.vk.com/authorize?client_id={appId}&scope=wall,photos,offline&redirect_uri=http://oauth.vk.com/blank.html&display=page&response_type=token
vkToken = "5de2747dc7f337856a4f9eaa1bb7ebe8f809f691b2bb6b04586734037da57a53e7540c263ff0e3fc3807"

#EyeEm token
eyeEmToken = "1d458eb10a2cc545790ff3748c2acff567fce124"

def main():
    try:
        logging.basicConfig(format = '%(asctime)s.%(msecs)d %(levelname)s %(message)s',
                            datefmt = '%Y-%m-%d %H:%M:%S',
                            filename = 'TwVk.log',
                            level = logging.INFO)
        logging.info('Script started')

        url = "https://userstream.twitter.com/1.1/user.json"
        param = {"delimited":"length", "with":"user"}
        header = {}

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        auth.apply_auth(url, "POST", header,param)

        logging.info('Twitter authorization successful')

        req = urllib2.Request(url)
        req.add_header("Authorization", header["Authorization"])
        r = urllib2.urlopen(req, urllib.urlencode(param), 90)

        while True:
            try:
                len = ""
                while True:
                    c = r.read(1)
                    if c=="\n": break
                    if c=="": raise Exception
                    len += c
                len = len.strip()
                if not len.isdigit(): continue
                t = json.loads(r.read(int(len)))

                if "user" in t and "text" in t and "created_at" in t and "id" in t:
                    handleTweet(t)
            except:
                logging.exception('Exception')
    except:
        logging.exception('Main exception')

def handleTweet(tweet):
    logging.info('Starting handleTweet')
    text = tweet["text"]
    logging.info('Tweet text: ' + text)
    if not text.startswith('@') and not "@zzeneg" in text):
        urls = tweet["entities"]["urls"]
        eyeEmId = ""

        for url in urls:
            text = text.replace(url["url"], url["expanded_url"])
            if url["expanded_url"].startswith("http://www.eyeem.com/p/"):
                eyeEmId = url["expanded_url"].replace("http://www.eyeem.com/p/", "")
                logging.info('EyeEm Id: ' + eyeEmId)
        logging.info('Tweet text with urls: ' + text)
        attachments = ""

        if "media" in tweet["entities"]:
            photo = tweet["entities"]["media"][0]
            logging.info('Photo found. Url: ' + photo["media_url"])
            text = text.replace(photo["url"], "")
            attachments = uploadPhoto(photo["media_url"])

        if (eyeEmId != ""):
            photoUrl = getEyeEmPhotoUrlById(eyeEmId)
            logging.info('Photo found. Url: ' + photoUrl)
            attachments = uploadPhoto(photoUrl)

        logging.info('Attachments: ' + attachments)
        vkMethod('wall.post', {'message': text,'attachments':attachments})
        logging.info('Posted to VK')
    else:
        logging.info('Skipping tweet')

def uploadPhoto(fileUrl):
    logging.info('Start uploading photo')
    response = vkMethod('photos.getWallUploadServer')
    uploadUrl = response['response']['upload_url']
    logging.info('Get upload url: ' + uploadUrl)
    urllib.urlretrieve(fileUrl,'temp.jpg')
    logging.info('Photo saved on local drive')
    files = {'photo': open('temp.jpg', 'rb')}
    response = requests.post(uploadUrl, files = files).json
    logging.info('Photo uploaded')
    response = vkMethod('photos.saveWallPhoto', response)
    logging.info('Photo saved in wall album')
    return response['response'][0]['id']

def vkMethod(method, data={}):
    url = 'https://api.vk.com/method/%s.json' % (method)
    data.update({'access_token': vkToken})

    response = requests.post(url, data).json

    if 'error' in response:
        error = response['error']
        logging.error('API: error (%s)' % (error['error_msg']))

    return response

def getEyeEmPhotoUrlById(id):
    url = "https://www.eyeem.com/api/v2/photos/{0}?access_token={1}".format(id, eyeEmToken)
    response = requests.get(url).json
    return response['photo']['photoUrl']

main()

