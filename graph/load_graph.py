import csv
from os import walk
from graph.graph import Graph


def load_review_graph() -> Graph:
    """Return a movie review graph corresponding to the given dataset.

    The movie review graph stores one vertex for each user and movie in the dataset.
    Each vertex stores as its item either a user name or film title.

    Edges represent a POSITIVE (>= 6) review between a user and a movie.
    """
    graph = Graph()

    films = create_films_list()

    for film in films:
        load_film_vertex(graph, film)

    return graph


def load_film_vertex(graph: Graph, movie_file: str) -> Graph:
    """Add a vertex on graph for the movie_file and a vertex for
    every user that gave it a positive review. The edge will contain the score
    given by the user.

    Preconditions:
        - movie_file is the path to a CSV file corresponding
        to the movie review data format described on the project written report.
    """
    with open('data/2_reviews_per_movie_raw/' + movie_file, encoding='utf8') as file:
        reader = csv.reader(file)
        next(file)

        for row in reader:
            user_name, score = row[0], row[1]
            if score != 'Null' and int(score) >= 6:  # only consider positive reviews
                graph.add_vertex(user_name, 'user')
                graph.add_vertex(clean(movie_file), 'movie')
                graph.add_edge(user_name, clean(movie_file), int(score))

    return graph


def add_user_info(username: str, film_ratings: dict) -> None:
    """For every film username has reviewed, add an extra row in its csv file
    containing username and the rating for this film."""

    for film in film_ratings:
        with open('data/2_reviews_per_movie_raw/' + unclean(film), 'a+',
                  newline='', encoding='utf8') as file:
            writer = csv.writer(file)
            writer.writerow([username, str(film_ratings[film])])


def create_films_list(to_clean: bool = False) -> list[str]:
    """Create a list containing all of the movies' names that are in the dataset.

    If to_clean is true, return the movies names without the .csv extension and add parenthesis
    between the date"""
    _, _, movie_names = next(walk('data/2_reviews_per_movie_raw'))
    if to_clean:
        return [clean(movie) for movie in movie_names]
    return movie_names


def clean(movie: str) -> str:
    """Return movie name without the .csv extension and add parenthesis
    between the date

    >>> clean('Some Like It Hot 1959.csv')
    'Some Like It Hot (1959)'
    """
    # remove dot and add parenthesis at the end
    movie = movie[:movie.index('.')] + ')'

    # add missing parenthesis and return
    return movie[:-5] + '(' + movie[-5:]


def unclean(movie: str) -> str:
    """Return movie name with the .csv extension and remove the parenthesis
    between the date

    >>> unclean('Some Like It Hot (1959)')
    'Some Like It Hot 1959.csv'
    """
    # remove parenthesis
    movie = movie.replace('(', '')
    movie = movie.replace(')', '')

    # add .csv extension
    return movie + '.csv'


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'extra-imports': ['graph', 'os', 'csv'],
        'allowed-io': ['add_user_info', 'load_film_vertex'],
        'max-line-length': 100,
        'disable': ['R1705', 'C0200']
    })

    import python_ta.contracts
    python_ta.contracts.check_all_contracts()

    import doctest

    doctest.testmod()
