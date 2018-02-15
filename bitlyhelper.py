from urllib.request import urlopen
import json
import config

TOKEN = config.bitly_token
ROOT_URL = 'https://api-ssl.bitly.com'
SHORTEN = '/v3/shorten?access_token={}&longUrl={}'

class BitlyHelper:

    def shorten_url(self, longurl):
        try:
            url = ROOT_URL + SHORTEN.format(TOKEN, longurl)
            response = urlopen(url).read().decode('utf-8')
            json_response = json.loads(response)
            return json_response['data']['url']
        except Exception as e:
            print(e)
