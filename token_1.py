import requests
import dotenv
from os import getenv

client_id='your_client_id'
client_secret='your_client_secret'

url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
response = requests.post(url)
print(response.text)
