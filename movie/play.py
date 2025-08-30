import requests

url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"

headers = {"accept": "application/json"}

response = requests.get(url, headers=headers)

print(response.text)