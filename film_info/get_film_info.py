import os
from urllib.request import urlretrieve
from omdbapi.movie_search import GetMovie


def get_film_info(movie_name: str) -> dict:
    """Return a dictionary containing the title, cast, director, rating, and
    synopsis of movie_name.

    Preconditions:
        - movie_name corresponds to a movie that is on the .csv dataset
        - movie_name[:-4] != '.csv'
    """
    movie = GetMovie(api_key='65e1cf9b')
    movie.get_movie(title=movie_name[:-7])
    movie_info = movie.get_data('Title', 'Director', 'Actors', 'Imdbrating', 'Plot', 'Imdbid', 'Poster')

    download_poster(movie_info['imdbid'], movie_info['poster'])

    return {'title': movie_info['title'], 'cast': movie_info['actors'], 'director(s)': movie_info['director'],
            'rating': movie_info['imdbrating'], 'synopsis': movie_info['plot'], 'id': movie_info['imdbid']}


def download_poster(movie_id: str, poster_link: str) -> None:
    """Obtain the link to movie's poster and download it as a .jpg on the project's folder.

    Preconditions:
        - movie corresponds to a movie that is on the .csv dataset
    """
    urlretrieve(poster_link,
                       'data/posters/' + movie_id + '.jpg')

def clean_films() -> None:
    """Deletes all files in data/posters"""
    folder = 'data/posters'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['movieposters', 'requests', 'imdb'],
        'allowed-io': ['download_poster'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest

    doctest.testmod()
