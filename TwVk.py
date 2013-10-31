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

#Main method
def main():
    try:
        logging.basicConfig(format = '%(asctime)s.%(msecs)d %(levelname)s %(message)s',
                            datefmt = '%Y-%m-%d %H:%M:%S',
                            filename = 'TwVk.log',
                            level = logging.INFO)
        logging.info('Script started')

        #authorization in twitter
        url = "https://userstream.twitter.com/1.1/user.json"
        param = {"delimited":"length", "with":"user"}
        header = {}
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        auth.apply_auth(url, "POST", header,param)

        logging.info('Twitter authorization successful')

        #getting tweets
        req = urllib2.Request(url)
        req.add_header("Authorization", header["Authorization"])
        r = urllib2.urlopen(req, urllib.urlencode(param), 90)

        #reading responses
        while True:
            try:
                #get response length
                length = ""
                while True:
                    c = r.read(1)
                    if (c == "\n") or (c == ""): break
                    length += c
                length = length.strip()
                if not length.isdigit(): continue
                #read response with length
                tweet = json.loads(r.read(int(length)))

                #if it's a tweet - start handling it
                if "user" in tweet and "text" in tweet and "created_at" in tweet and "id" in tweet:
                    handleTweet(tweet)
            except:
                logging.exception('Exception')
    except:
        logging.exception('Main exception')

#Method handling tweet
def handleTweet(tweet):
    logging.info('Starting handleTweet')
    #get tweet text
    text = tweet["text"]
    logging.info('Tweet text: ' + text)
    #check for answer, retweet or mention
    if not text.startswith('@') and not "@zzeneg" in text:
        #get urls in tweet
        urls = tweet["entities"]["urls"]
        eyeEmId = ""
        attachments = ""

        #replace shortened urls
        for url in urls:
            text = text.replace(url["url"], url["expanded_url"])
            #if it's EyeEm photo - get it id
            if url["expanded_url"].startswith("http://eyeem.com/p/"):
                eyeEmId = url["expanded_url"].replace("http://eyeem.com/p/", "")
                logging.info('EyeEm Id: ' + eyeEmId)
                photoUrl = getEyeEmPhotoUrlById(eyeEmId)
                logging.info('Photo found. Url: ' + photoUrl)
                attachments = uploadPhoto(photoUrl)

        logging.info('Tweet text with urls: ' + text)

        #if photo is attached - remove it and upload to VK
        if "media" in tweet["entities"]:
            photo = tweet["entities"]["media"][0]
            logging.info('Photo found. Url: ' + photo["media_url"])
            text = text.replace(photo["url"], "")
            attachments = uploadPhoto(photo["media_url"])

        logging.info('Attachments: ' + attachments)
        #post to VK and attach photo ID
        #vkMethod('wall.post', {'message': text,'attachments':attachments})
        logging.info('Posted to VK')
    else:
        logging.info('Skipping tweet')

#Method uploading photo to VK
def uploadPhoto(fileUrl):
    logging.info('Start uploading photo')
    #get url for uploading photo
    response = vkMethod('photos.getWallUploadServer')
    uploadUrl = response['response']['upload_url']
    logging.info('Get upload url: ' + uploadUrl)
    #saving photo locally
    urllib.urlretrieve(fileUrl,'temp.jpg')
    logging.info('Photo saved on local drive')
    #uploading photo to VK
    files = {'photo': open('temp.jpg', 'rb')}
    response = requests.post(uploadUrl, files = files).json()
    logging.info('Photo uploaded')
    #add photo in wall album
    response = vkMethod('photos.saveWallPhoto', response)
    logging.info('Photo saved in wall album')
    #return photo ID
    return response['response'][0]['id']

#Common VK API method
def vkMethod(method, data={}):
    url = 'https://api.vk.com/method/%s.json' % (method)
    data.update({'access_token': vkToken})

    response = requests.post(url, data).json()

    if 'error' in response:
        error = response['error']
        logging.error('API: error (%s)' % (error['error_msg']))

    return response

#Method getting photo URL from EyeEm
def getEyeEmPhotoUrlById(photoId):
    url = "https://www.eyeem.com/api/v2/photos/{0}?access_token={1}".format(photoId, eyeEmToken)
    response = requests.get(url).json()
    return response['photo']['photoUrl']

main()