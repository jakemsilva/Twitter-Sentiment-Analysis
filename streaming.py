#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

#Variables that contains the user credentials to access Twitter API 
access_token = "378346315-OpmfXLakwRDKdGLgyRGkpQBBuumEptiOfo82Trpm"
access_token_secret = "oDIsqcKHLjLJibjIj01LTIyFPgKYg7TZRzpf39GEx1eUT"
consumer_key = "LnMXOPAy9QglEYPZFGYLu2Y1U"
consumer_secret = "UgocwcwSyJXPyglxrTbJ702LUk2hXmBBsAC4DQkfWpkDVYeLWk"


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):
 
    def on_data(self, data):
        print(data)
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    stream.filter(track=['rutgers', 'michigan'])