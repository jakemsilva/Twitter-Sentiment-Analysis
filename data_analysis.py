import json
import pandas as pd
import matplotlib.pyplot as plt
import re
from html.parser import HTMLParser
from nlp_processing import *
from DictionaryTagger import *
from datetime import datetime
from datetime import timedelta
import sys
import codecs
RELAVANT_WORDS = ('football', 'win', 'lose', 'game', 'big house', 'pass', 'touchdown', 'interception', 'run', 'quarterback', 'refs', 'yards', 'rutgers')

def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print (*objects, sep=sep, end=end, file=file)
    else:
        f = lambda obj: str(obj).encode(enc, errors='backslashreplace').decode(enc)
        print (*map(f, objects), sep=sep, end=end, file=file)

sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

def word_in_text(text):
    text = text.lower()
    for word in RELAVANT_WORDS:
        match = re.search(word, text)
        if match:
            return True
    return False

def clean_text(text):
	#text = html_parser.unescape(text)	
	#tweet = text.decode('unicode_escape').encode('ascii','ignore')
	tweet = re.sub(r"(?:\@|https?\://)\S+", "", text)
	encodedTweet = tweet.lower()
	return encodedTweet

def value_of(sentiment):
    if sentiment == 'positive': return 1
    if sentiment == 'negative': return -1
    return 0
    
def sentence_score(sentence_tokens, previous_token, acum_score):    
    if not sentence_tokens:
        return acum_score
    else:
        current_token = sentence_tokens[0]
        tags = current_token[2]
        token_score = sum([value_of(tag) for tag in tags])
        if previous_token is not None:
            previous_tags = previous_token[2]
            if 'inc' in previous_tags:
                token_score *= 2.0
            elif 'dec' in previous_tags:
                token_score /= 2.0
        return sentence_score(sentence_tokens[1:], current_token, acum_score + token_score)

def sentiment_score(review):
    return sum([sentence_score(sentence, None, 0.0) for sentence in review])

def convertTime(time):
    clean_timestamp = datetime.strptime(time,'%a %b %d %H:%M:%S +0000 %Y')
    offset_hours = -5 #offset in hours for EST timezone

    #account for offset from UTC using timedelta                                
    local_timestamp = clean_timestamp + timedelta(hours=offset_hours)
    final_timestamp =  datetime.strftime(local_timestamp, '%Y-%m-%d %I:%M:%S %p')  
    return local_timestamp

tweets_data_path = 'rutgers_michigan.txt'

tweets_data = []
tweets_file = open(tweets_data_path, "r")
for line in tweets_file:
    try:
        tweet = json.loads(line)
        cleaned_text = clean_text(tweet['text'])
        created = convertTime(tweet['created_at'])
        tweets_data.append({'text': cleaned_text, 'created': created, 'coordinates': tweet['coordinates'], 'location': tweet['user']['location'], 'relevant': word_in_text(cleaned_text)})
    except:
        continue

i = 0
n = 10060
splitter = Splitter()
postagger = POSTagger()

dicttagger = DictionaryTagger([ 'dicts/positive.yml', 'dicts/negative.yml', 'dicts/inc.yml', 'dicts/dec.yml', 'dicts/inv.yml'])
taggedData = []

for tweet in tweets_data:
	if tweet['relevant'] and tweet['created'] > datetime(2015, 11, 7, 15, 42, 0) and tweet['created'] < datetime(2015, 11, 7, 19, 4, 10):	
		i += 1
		splitted_sentences = splitter.split(tweet['text'])
		pos_tagged_sentences = postagger.pos_tag(splitted_sentences)
		dict_tagged_sentences = dicttagger.tag(pos_tagged_sentences)
		tweet['tagged'] = dict_tagged_sentences
		tweet['sentiment_score'] = sentiment_score(dict_tagged_sentences)
				
		data = {		
			'text' : tweet['text'],
			'sentiment_score' : tweet['sentiment_score'],
			'created' : datetime.strftime(tweet['created'], '%Y-%m-%d %I:%M:%S %p')
		}
		sys.stdout.write("\r{0}".format((float(i)/n)*100))
		sys.stdout.flush()
		taggedData.append(data)

with open('final_data.txt', 'w') as outfile:
    json.dump(taggedData, outfile)


"""
tweets = pd.DataFrame()

tweets['text'] = map(lambda tweet: tweet['text'], tweets_data)
tweets['created_at'] = map(lambda tweet: tweet['created_at'], tweets_data)
tweets['coordinates'] = map(lambda tweet: tweet['coordinates'] if tweet['coordinates'] != None else None, tweets_data)
tweets['location'] = map(lambda tweet: tweet['user']['location'] if tweet['user']['location'] != None else None, tweets_data)
tweets['relevant'] = tweets['text'].apply(lambda tweet: word_in_text('football', tweet) or word_in_text('win', tweet) or word_in_text('lose', tweet) or word_in_text('game', tweet))
"""
#print(tweets['text'].value_counts()[True])