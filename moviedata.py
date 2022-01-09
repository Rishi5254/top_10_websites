import requests


def search(movie_name):
    parameters = {
        'api_key': '0831005b836fca6472acac98e025e8a7',
        'language': 'en-US',
        'query': movie_name,
    }
    data = requests.get(url='https://api.themoviedb.org/3/search/movie', params=parameters).json()['results'][0]
    return data
