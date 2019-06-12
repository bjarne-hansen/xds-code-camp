# Import the python requests package
# pip install requests
# See https://2.python-requests.org/en/master/
import requests

r = requests.get('http://localhost:5000')
print("Response from http://localhost:5000\n  {}".format(r.text))

r = requests.get('http://localhost:5000?message=Bonjour Monsieur!')
print("Response from 'http://localhost:5000?message=Bonjour Monsieur!\n  {}".format(r.text))
