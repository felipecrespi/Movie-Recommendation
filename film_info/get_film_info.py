"""
CSC111 Winter 2021 Final Project: get_film_info

Information about get_film_info:
===============================
Responsible for the information of a given film. Using the imdb and moveiposters libraries,
it is responsible for obtaining the title, movie poster, director, cast, rating,
and synopsis of the films given.


Copyright and Usage Information
===============================
This file is provided solely for the personal and private use of students
taking CSC111 at the University of Toronto St. George campus. All forms of
distribution of this code, whether as given or with any changes, are
expressly prohibited. For more information on copyright for CSC111 materials,
please consult our Course Syllabus.

This file is Copyright (c) 2020 Felipe Benevides Crespi
"""

import imdb
import movieposters as mp
import requests
import os


def get_film_info(movie_name: str) -> dict:
    """Return a dictionary containing the title, cast, director, rating, and
    synopsis of movie_name.

    Preconditions:
        - movie_name corresponds to a movie that is on the .csv dataset
        - movie_name[:-4] != '.csv'
    """
    ia = imdb.IMDb()
    movie = []
    while (len(movie) < 1):
        movie = ia.search_movie(movie_name[:-7])
    movie = ia.get_movie(movie[0].getID())

    # Note: ia.search_movie(movie)[0] was supposed to be enough for the Movie object,
    # but for some reason it did not have the necessary information. This is why I used
    # it only to get the id so I could create a new Movie object directly
    # (instead of through the searching method)

    cast = []
    i = 0
    for actor in movie['cast']:
        if i > 5:
            # as far as I understand, movie['cast'] is sorted in terms of the actors'
            # relevance to the film; thus only the 5 most important will be displayed.
            break
        cast.append(actor['name'])
        i += 1

    directors = []
    for director in movie['director']:
        directors.append(director['name'])

    download_poster(movie.getID())

    return {'title': movie_name, 'cast': cast, 'director(s)': directors,
            'rating': movie['rating'], 'synopsis': movie['plot'], 'id': movie.getID()}


def download_poster(movie: str) -> None:
    """Obtain the link to movie's poster and download it as a .jpg on the project's folder.

    Preconditions:
        - movie corresponds to a movie that is on the .csv dataset
    """
    poster_link = mp.get_poster(id='tt' + movie)
    # movieposters considers 'tt' to be part of every iMDB film id

    with open('data/posters/' + movie + '.jpg', 'wb') as handle:
        response = requests.get(poster_link, stream=True)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)


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
