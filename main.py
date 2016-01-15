__author__ = 'WTT'

import tweepy
from tweepy import OAuthHandler
import collections
import re
import csv
from imageProcessing import *
import PIL






consumer_key = 'ou0Sw4GQqc497wyHcrtPksL9I'
consumer_secret = 'mpAeMD2SYUXdvkPQGJH4DPhdyPCmlm03I6NMw0g8nhwMcARDGK'
access_token = '38263001-QDabDYVx3Aa9wSNfNnbXmoI3J3B1lVOle0DSpLpof'
access_secret = 'SrOZdvyLwnNBaK1E08rXXkd15CpjVrXyROfpuOBNJx2Vw'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)

#for testing purposes. Do not want to exceed API rate
x = raw_input('Parse new tweets? (y/n)')

if x == 'y':
    rawTweets = []
    user = raw_input("Please provide a twitter account to parse: ")
    f = open('myTweets.txt', 'w')

    #tweet retreival from https://gist.github.com/yanofsky/5436496
    #self written code for testing only allowed for my own tweets to be read
    new_tweets = api.user_timeline(screen_name=user, count=200)
    rawTweets.extend(new_tweets)
    oldest = rawTweets[-1].id - 1
    while len(new_tweets) > 0:

        new_tweets = api.user_timeline(screen_name=user, count=200,max_id=oldest)
        rawTweets.extend(new_tweets)
        oldest = rawTweets[-1].id - 1
        print 'Tweets parsed: ', (len(rawTweets)), '...\r',

    outTweets = [[tweet.text.encode("utf-8")] for tweet in rawTweets]

    with open('parsed_tweets.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(outTweets)

    pass

fname = 'myTweets.txt'

rgx = re.compile("(\w[\w']*\w|\w)")


#for the purposes of keeping things easy, stopwords are local.
stop = ['a','able','about','across','after','all','almost','also','am','among',
             'an','and','any','are','as','at','be','because','been','but','by','can',
             'cannot','could','dear','did','do','does','either','else','ever','every',
             'for','from','get','got','had','has','have','he','her','hers','him','his',
             'how','however','i','if','in','into','is','it','its','just','least','let',
             'like','likely','may','me','might','most','must','my','neither','no','nor',
            'not','of','off','often','on','only','or','other','our','own','rather','said',
             'say','says','she','should','since','so','some','than','that','the','their',
             'them','then','there','these','they','this','tis','to','too','twas','us',
             'wants','was','we','were','what','when','where','which','while','who', 'u', 'amp',
             'whom','why','will','with','would','yet','you','your', "i'm", 'rt', "it's"]

tweetText = []
with open('parsed_tweets.csv', 'rb') as f:
    reader = csv.reader(f, delimiter=' ', quotechar='|')
    for row in reader:
        for each in row:
            #filtering mentions/hash tags
            if '@' in each or '#' in each:
                continue

            #filtering links
            each = re.sub(r'^https?:\/\/.*[\r\n]*', '', each, flags=re.MULTILINE)
            each = rgx.findall(each)

            #making them all lowercase and adding words to list
            for word in each:
                word = word.lower()
                if word not in stop and word != 'u':
                    tweetText.append(word)

#counting up the most popular words
counter = collections.Counter(tweetText)
commonCount = 50
mostCommon = counter.most_common(commonCount)

#might do something with this later(statistics logging?)
#for each in mostCommon:
   #print each


print 'Finding letters...'
letterImages = []
#make an array where ('lol',30) becomes ([l.jpg, o.jpg, l.jpg], 30)
for each in mostCommon:
    word = each[0]
    magnitude = each[1]
    letterImages.append([prepare(word), magnitude])

wordImages = []

print 'Assembling words...'

#make an array where ([l.jpg, o.jpg, l.jpg], 30) becomes ( lol.jpg, magnitude)
for each in letterImages:
    letters = each[0]
    magnitude = each[1]
    width = 0
    height = 0
    #find the dimensions of the word in the first pass
    for char in letters:
        width += char.size[0]
        if char.size[1] >= height:
            height = char.size[1]

    #paste the letters onto it on the second pass
    wordImage = Image.new('RGBA', (width, height), (0, 255, 0, 255))
    x = 0
    for char in letters:
        x2 = x + char.size[0]
        wordImage.paste(char, (x, 0, x2, char.size[1]))
        x += char.size[0]

    wordImages.append([wordImage, magnitude])


# each entry in the wordImages array is now of the form ('wordImagefile.png', magnitude)
# the next step is to chroma key these images and give the letters a random color.
print 'Chroma Keying and Coloring words...\r',
count = 0
for each in wordImages:
    color = randomColor()
    image = each[0]
    output = Image.new("RGBA", image.size)
    for y in xrange(image.size[1]):
        for x in xrange(image.size[0]):
            p = image.getpixel((x, y))
            r = p[0]
            g = p[1]
            b = p[2]

            if r <= b <= 10 <= 250 <= g:
                output.putpixel((x, y), (255, 255, 255, 255))

            else:
                output.putpixel((x, y), color)

    #postMask = Image.new("RGBA", output.size, (255, 255, 255, 255))
    #postMask.paste(output, mask=output)
    each[0] = output
    count += 1
    print 'Chroma Keying and Coloring words...', count, ' of ', commonCount, '\r',

print 'Assembling cloud...'


#deciding the width of our cloud
cloudWidth = 0
cloudHeight = 700
topWord = wordImages[0][0]
topwidth = topWord.size[0]

widths = [int(wordImages[1][0].size[0] * 0.5),
          int(wordImages[2][0].size[0] * 0.5),
          int(wordImages[3][0].size[0] * 0.6),
          int(wordImages[4][0].size[0] * 0.7),
          int(wordImages[5][0].size[0] * 0.35 * 0.85),
          int(wordImages[6][0].size[0] * 0.7 * 0.85),
          int(wordImages[7][0].size[0] * 0.35 * 0.7),
          int(wordImages[8][0].size[0] * 0.7 * 0.7),
          int(wordImages[9][0].size[0] * 0.35 * 0.6),
          int(wordImages[10][0].size[0] * 0.7 * 0.6)]


maxWidth = max(widths)
#pairings are 1+5, and 2+6, odds left, evens right
cloudWidth = widths[1] + widths[5]

if widths[2] + widths[6] > cloudWidth:
    cloudWidth = widths[2] + widths[6]

if maxWidth*1.5 + topwidth > cloudWidth:
    cloudWidth = int(maxWidth*1.5 + topwidth)



cloud = Image.new("RGBA", (cloudWidth, cloudHeight), (255, 255, 255, 255))
area = cloudWidth*cloudHeight
fsum = 0.0

for each in wordImages:
    fsum += each[1]

#most popular word's gonna be front and center.

topWord = wordImages[0][0]
topwidth = topWord.size[0]
topheight = topWord.size[1]

xpos = (cloudWidth - topwidth) / 2
ypos = (cloudHeight - topheight) / 2

offset = (xpos, ypos)

topArea = topwidth * topheight

cloud.paste(topWord, offset)
rank = 1


while rank < commonCount:
    if rank > 10:
        break
    word = wordImages[rank][0]
    width = word.size[0]
    height = word.size[1]
    mag = wordImages[rank][1]
    ratio = mag/wordImages[rank-1][1]

    word = word.resize((int(width/2), int(height/2)), PIL.Image.ANTIALIAS)
    width = word.size[0]
    height = word.size[1]

    if rank == 1:
        cloud.paste(word, (xpos + (topwidth/2), ypos - height))
    if rank == 2:
        word = word.resize((int(width*0.8), int(height*0.8)), PIL.Image.ANTIALIAS)
        width = word.size[0]
        height = word.size[1]
        cloud.paste(word, (xpos + (topwidth/2) - width, ypos + topheight))
    if rank > 2 and rank % 2 != 0:
        word = word.resize((int(width*0.7), int(height*0.7)), PIL.Image.ANTIALIAS)
        width = word.size[0]
        height = word.size[1]
        if rank == 3:
            cloud.paste(word, (xpos - width, ypos))
            height7 = ypos + height
        if rank == 5:
            word = word.resize((int(width*0.85), int(height*0.85)), PIL.Image.ANTIALIAS)
            width = word.size[0]
            height = word.size[1]
            cloud.paste(word, (xpos + (topwidth/2) - width, ypos - height))
        if rank == 7:
            word = word.resize((int(width*0.7), int(height*0.7)), PIL.Image.ANTIALIAS)
            width = word.size[0]
            height = word.size[1]
            cloud.paste(word, (xpos - width, height7))
            height9 = height7 + height
        if rank == 9:
            word = word.resize((int(width*0.6), int(height*0.6)), PIL.Image.ANTIALIAS)
            width = word.size[0]
            height = word.size[1]
            cloud.paste(word, (xpos - width, height9))

    if rank > 2 and rank % 2 == 0:
        word = word.resize((int(width*0.60), int(height*0.60)), PIL.Image.ANTIALIAS)
        width = word.size[0]
        height = word.size[1]
        if rank == 4:
            cloud.paste(word, (xpos + topwidth, ypos + topheight - height))
            height8 = ypos + topheight - (2*height)

        if rank == 6:
            word = word.resize((int(width*0.85), int(height*0.85)), PIL.Image.ANTIALIAS)
            width = word.size[0]
            height = word.size[1]
            cloud.paste(word, (xpos + (topwidth/2), ypos + topheight))
        if rank == 8:
            word = word.resize((int(width*0.7), int(height*0.7)), PIL.Image.ANTIALIAS)
            width = word.size[0]
            height = word.size[1]
            cloud.paste(word, (xpos + topwidth, height8))
            height10 = height8 - height
        if rank == 10:
            word = word.resize((int(width*0.6), int(height*0.6)), PIL.Image.ANTIALIAS)
            width = word.size[0]
            height = word.size[1]
            cloud.paste(word, (xpos + topwidth, height10))

    topMag = wordImages[0][1]
    rank += 1

background = Image.new("RGBA", (cloudWidth, cloudHeight), (255, 255, 255, 100))
faded = Image.new("RGBA", (cloudWidth, cloudHeight), (255, 255, 255, 255))

print 'Creating background...'

bWords = wordImages[rank:]
rows = 31
wordCount = len(bWords)
w = 0
#make the words smaller
for each in bWords:
    word = each[0]
    width = word.size[0]
    height = word.size[1]
    bWords[w] = word.resize((int(width/10), int(height/10)), PIL.Image.ANTIALIAS)
    w += 1

#populate background with less comon words
w = 0
lastWord = ''
for x in range(0, 32):
    length = cloudWidth
    offset = 0
    if lastWord == bWords[w % wordCount] or lastWord == bWords[(w + 1) % wordCount] or lastWord == bWords[(w - 1) % wordCount]:
        w += 2
    while offset < length:
        currentWord = bWords[w % wordCount]
        background.paste(currentWord, (offset, x * 28))
        offset += currentWord.size[0] + 20
        w += 1
    lastWord = currentWord = bWords[(w - 1) % wordCount]

#fade them a little bit
background.save("background.png", "PNG")
mask = background.convert("L").point(lambda x: min(x, 50))
background.putalpha(mask)
faded.paste(background, (0, 0), background)
faded.save("background2.png", "PNG")

#time to assemble the final image
print 'Combing top ranking words with minor words...'
image = cloud
for y in xrange(image.size[1]):
        for x in xrange(image.size[0]):
            p = image.getpixel((x, y))
            r = p[0]
            g = p[1]
            b = p[2]

            if r == 255 and g == 255 and b == 255:
                image.putpixel((x, y), (255, 255, 255, 0))

faded.paste(image, mask=image)
faded.show()
faded.save("cloudPicFinal.png", "PNG")
cloud.save("cloud.png", "PNG")
