from tkinter import *
from PIL import ImageTk, Image
import pickle
import os
import sys

from graph.load_graph import create_films_list, add_user_info, load_review_graph
from graph.graph import Graph
from film_info.get_film_info import get_film_info, clean_films
from film_info.recommend_films import recommend_movies


def break_into_lines(text: str, i: int) -> str:
    """Add \n to text after i lines and return it. Round it to the next white space"""
    j = 1
    while j * i < len(text):
        index = text[j*i:].index(' ') + (j * i)
        text = text[:index] + '\n' + text[index:]
        j += 1
    return text


class _SearchBox(Frame):
    """A listbox of movies that updates as the user types in a search box.

    Instance Attributes:
        - selected_film: the str of the current option selected
        - choices: list of the items to be on the listbox

        - entryVar: a StringVar to be user on entry
        - entry: an Entry wherein the user types the movies' names
        - listbox: a Listbox containing all the movies
    """
    selected_film: str
    choices = list

    entryVar: StringVar
    entry: Entry
    listbox: Listbox

    def __init__(self) -> None:
        Frame.__init__(self, root, bg='#363636')

        self.selected_film = ''

        self.choices = create_films_list(True)

        self.entryVar = StringVar()
        self.entry = Entry(self, textvariable=self.entryVar, bg='white', borderwidth=0)
        self.listbox = Listbox(self, height=6, width=75, bg='#363636', fg='white', borderwidth=0)
        self.listbox.insert('end', *self.choices)

        self.entry.pack(side=TOP, fill='x')
        self.listbox.pack(side=TOP, fill='both', expand=True)

        self.entryVar.trace("w", self.show_choices)
        self.listbox.bind("<<ListboxSelect>>", self.on_listbox_select)

    def on_listbox_select(self, event) -> None:
        """Set the value based on the item that was clicked"""
        item = self.listbox.curselection()
        if len(item) > 0:
            item = self.listbox.get(item[0])
            self.entryVar.set(item)
            self.selected_film = item

    def show_choices(self, name1, name2, op) -> None:
        """Filter choices based on what was typed in the entry"""
        pattern = self.entryVar.get().upper()
        choices = [x for x in self.choices if x.upper().startswith(pattern)]
        self.listbox.delete(0, 'end')
        self.listbox.insert('end', *choices)

    def get_selected_film(self) -> str:
        """Filter choices based on what was typed in the entry"""
        return self.selected_film


class Project(Frame):
    """The visual interaction of the project

    Instance Attributes:
        - list_films: a dictionary containing the user's films (keys) and
        the score they gave to each of them (values)

        - top: frame containing username box
        - type_username: label to indicate the user to type their name
        - username_box: entry wherein user types their name
        - agree_button_var: an IntVar to be check if agree_button has been clicked on
        - agree_button: a Checkbutton regarding the user's choice to share their information

        - middle: frame containing a _SearchBox and a Listbox to
        allow the user to search for, choose, rate, and add movies to their list
        - search_box: a _SearchBox (see _Searchbox docstring)
        - rating_box: a Listbox containing the possible rating a user can give to the film
        - add_movie_button: a Button that add the chosen film and its score to list_films
        - search_text: Label indicating the user wat to do on the searchbox
        - search_frame: Frame containing the search_box and rating_box

        - bottom: Frame visually representing the current list_films
        - list_label: Label indicating the number of films still to be selected and whether
        the user can advance ot not
        - current_list: Frame containing the Labels of the films in the current list_films
        - advance_button: a Button that destroys every element in the current frame and
        initialized the recommendation section of the program

        - recommended_films_frame: a list of individual film Frames
        - recommended_text: Label indicating that the recommended films are being shown
        - recommended_list: list containing all the recommended films, including those not
        being shown
        - update_recommendations_button: a Button that updates the window to show the
        next five films in recommended_list
        - recommended_frame: Frame containing all the elements in the recommendation section
    """
    graph: Graph
    list_films: dict[str, int]

    # Widgets of the first frame
    top: Frame
    type_username: Label
    username_box: Entry
    agree_button_var: IntVar
    agree_button: Checkbutton

    middle: Frame
    search_box: _SearchBox
    rating_box: Listbox
    add_movie_button: Button
    add_movie_button_image: PhotoImage
    search_text: Label
    search_frame: Frame

    bottom: Frame
    list_label: Label
    current_list: Frame
    advance_button_image: PhotoImage
    advance_button: Button

    def __init__(self) -> None:
        try:
            with open('data/graph.pkl', 'rb') as inp:
                self.graph = pickle.load(inp)
        except:
            self.graph = load_review_graph()

        Frame.__init__(self, root, bg='#363636')
        self.adv = False

        self.top = Frame(root, bg='#363636')
        self._init_top(self.top)
        self.top.pack(in_=self)  # pack it to the main frame at the top

        self.middle = Frame(root, bg='#363636')
        self._init_middle(self.middle)
        self.middle.pack(in_=self, pady=20)  # pack it to the main frame at the top

        self.bottom = Frame(root, bg='#363636')
        self._init_bottom(self.bottom)
        self.bottom.pack(in_=self)

        self.pack(expand='yes', fill='both')

    def _init_top(self, frame: Frame) -> None:
        """Initialize a new frame to contain the username box and the label and button
        related to it."""
        self.type_username = Label(root, text='Type your name:', bg='#363636', fg='white')
        self.type_username.config(font=('Arial', 20))
        self.type_username.pack(in_=frame, side=TOP)

        self.username_box = Entry(root, relief='flat', bg='white')
        self.username_box.pack(in_=frame, side=TOP)

        self.agree_button_var = IntVar()
        self.agree_button = Checkbutton(root, text='I agree with using my results'
                                                   ' to improve the algorithm.',
                                        variable=self.agree_button_var,
                                        bg='#363636', fg='white')
        self.agree_button.pack(in_=frame, side=TOP)

    def _init_middle(self, frame: Frame) -> None:
        """Initialize a new frame to contain a _SearchBox and a Listbox to
        allow the user to search for, choose, rate, and add movies to their list
        """
        self.search_text = Label(root, text='Search for your favourite films and '
                                            'add at least 5 to your list!',
                                 bg='#363636', fg='white')
        self.search_text.config(font=('Arial', 34))
        self.search_text.pack(in_=frame, side=TOP)

        self.search_frame = Frame(bg='#363636')
        self.search_box = _SearchBox()

        # create listbox and change its font.
        self.rating_box = Listbox(self.search_frame, height=5, width=5, relief='flat',
                                  fg='#ff0066', bg='#363636')
        self.rating_box.config(font=('Arial', 11))
        for i in range(6, 11):  # the user is only allowed to give positive reviews
            self.rating_box.insert(i, str(i) + ' ★')

        self.add_movie_button_image = ImageTk.PhotoImage(Image.open('buttons/add_btn.png').resize((50, 50)))

        self.add_movie_button = Button(self.search_frame, bg='#363636', cursor="hand2",
                                       image=self.add_movie_button_image,
                                       text='Add\nMovie', relief='flat', command=self.add_movie)

        self.search_box.pack(in_=self.search_frame, side=LEFT)
        self.rating_box.pack(in_=self.search_frame, side=LEFT, padx=15)
        self.add_movie_button.pack(in_=self.search_frame, side=LEFT, padx=30)

        self.search_frame.pack(in_=frame, side=BOTTOM, pady=10)

    def _init_bottom(self, frame: Frame) -> None:
        """Initialize a new frame to visually represent the current list of the user.
        This list is shown as each selected movie corresponding to a boxed label.
        """
        self.list_label = Label(root, text='Your current selected films. '
                                           'Please add at least 5 more.',
                                bg='#363636', fg='white')
        self.list_label.config(font=('Arial', 22))
        self.list_label.pack(in_=frame, side=TOP)

        self.list_films = {}

        self.current_list = Frame(root, bg='#363636')
        self.current_list.pack(in_=frame, side=TOP, pady=10)

    def add_movie(self) -> None:
        """Add a movie to the list_films and represent it visually in the frame current_list"""
        film_name = self.search_box.get_selected_film()
        film_rating = self.rating_box.get(self.rating_box.curselection())

        if film_name == '' or film_rating is None:
            return None

        self.list_films[film_name] = int(film_rating[:film_rating.index(' ')])

        # create a label to visually represent the chosen film
        film_label = Label(root, text=film_name + '\n' + film_rating,
                           borderwidth=2, relief='ridge', bg='#363636', fg='#ff0066')
        film_label.config(font=('Arial', 14))

        film_label.pack(in_=self.current_list, side=LEFT, padx=10)

        # after the movie is added, make sure the user cannot add it again
        self.search_box.choices.remove(film_name)
        self.search_box.entryVar.set('')

        films_remaining = 5 - len(self.list_films)
        if films_remaining > 0:
            self.list_label.configure(text='Your current selected films. '
                                           'Please add at least ' +
                                           str(films_remaining) + ' more.')
        elif films_remaining == 0:
            self.list_label.configure(text='Your current selected films. '
                                           'Click the button below to continue.\n'
                                           'You can choose to add more films, but this may '
                                           'make your list a little messy!')

            self.advance_button_image = ImageTk.PhotoImage(
                Image.open('buttons/continue_btn.png').resize((30, 30)))
            self.advance_button = Button(self, image=self.advance_button_image, cursor="hand2",
                                         command=self.advance,  bg='#363636', relief='flat')
            self.advance_button.pack(in_=self, side=TOP, pady=10)

    def advance(self) -> None:
        """If allowed, add user info to the dataset. Then, destroy all items visually
        shown in self and initiate and pack the widgets
        and frames related to recommendations.
        """
        if self.agree_button_var.get() == 1:  # if user agreed to share info
            add_user_info(self.username_box.get(), self.list_films)
            os.remove('data/graph.pkl')
        else:  # no new updates to graph, so we can save it for next time
            with open('data/graph.pkl', 'wb') as outp:
                sys.setrecursionlimit(0x1000000)
                pickle.dump(self.graph, outp, pickle.HIGHEST_PROTOCOL)

        self.top.destroy()
        self.middle.destroy()
        self.bottom.destroy()
        self.list_label.destroy()
        self.advance_button.destroy()

        self.destroy()
        try:
            with open('data/graph.pkl', 'rb') as inp:
                graph = pickle.load(inp)
        except:
            graph = load_review_graph()
        Result(self.list_films, graph)


class Result(Frame):
    """The visual interaction of the project

    Instance Attributes:
        - list_films: a dictionary containing the user's films (keys) and
        the score they gave to each of them (values)

        - top: frame containing username box
        - type_username: label to indicate the user to type their name
        - username_box: entry wherein user types their name
        - agree_button_var: an IntVar to be check if agree_button has been clicked on
        - agree_button: a Checkbutton regarding the user's choice to share their information

        - middle: frame containing a _SearchBox and a Listbox to
        allow the user to search for, choose, rate, and add movies to their list
        - search_box: a _SearchBox (see _Searchbox docstring)
        - rating_box: a Listbox containing the possible rating a user can give to the film
        - add_movie_button: a Button that add the chosen film and its score to list_films
        - search_text: Label indicating the user wat to do on the searchbox
        - search_frame: Frame containing the search_box and rating_box

        - bottom: Frame visually representing the current list_films
        - list_label: Label indicating the number of films still to be selected and whether
        the user can advance ot not
        - current_list: Frame containing the Labels of the films in the current list_films
        - advance_button: a Button that destroys every element in the current frame and
        initialized the recommendation section of the program

        - recommended_films_frame: a list of individual film Frames
        - recommended_text: Label indicating that the recommended films are being shown
        - recommended_list: list containing all the recommended films, including those not
        being shown
        - update_recommendations_button: a Button that updates the window to show the
        next five films in recommended_list
        - recommended_frame: Frame containing all the elements in the recommendation section
    """
    graph: Graph
    list_films: dict[str, int]

    # Widgets of the second frame
    recommended_films_frame: list[Frame]
    recommended_text: Label
    recommended_list: list
    recommended_frame: Frame

    update_recommendations_button: Button
    update_recommendations_button_image: PhotoImage

    def __init__(self, list_films: dict, graph: Graph) -> None:
        Frame.__init__(self, root, bg='#363636')
        self.list_films = list_films
        self.graph = graph
        self.update_recommendations_button_image = ImageTk.PhotoImage(
            Image.open('buttons/update_btn.png').resize((120, 30)))
        self.advance()

        self.pack(expand='yes', fill='both')

    def advance(self) -> None:
        """If allowed, add user info to the dataset. Then, destroy all items visually
        shown in self and initiate and pack the widgets
        and frames related to recommendations.
        """
        self.recommended_list = recommend_movies([*self.list_films], self.graph)
        self.recommended_films_frame = []
        self.recommended_frame = Frame(root, bg='#363636')
        self._init_recommendations(self.recommended_frame)

        self.recommended_frame.pack(in_=self, side=TOP)  # pack it to the main frame

    def _init_recommendations(self, frame: Frame) -> None:
        """Initialize a new frame to contain the recommended films. Each film will
        be shown in its individual frame, containing its poster and labels
        regarding its cast, director, synopsis, and average iMDB score.
        """
        self.recommended_text = Label(root, text='These are your recommendations!', bg='#363636', fg='white')
        self.recommended_text.config(font=('Arial', 34))
        self.recommended_text.pack(in_=frame, side=TOP)

        self.update_recommendations_button = Button(root, image=self.update_recommendations_button_image,
                                                    bg='#363636', relief='flat', cursor="hand2",
                                                    command=self._update_recommendations)
        self.update_recommendations_button.pack(in_=frame, side=TOP)

        for movie in self.recommended_list[:5]:
            info = get_film_info(movie)

            movie_frame = Frame(root, bg='#363636')

            # for some reason, some movie posters did not download properly
            # and it crashed the entire code. To avoid this, a simple label will be
            # added when the code cannot be found
            try:
                poster_image = ImageTk.PhotoImage(
                    Image.open('data/posters/' + info['id'] + '.jpg').resize((300, 400)))
                poster = Label(root, image=poster_image, bg='#363636')
                poster.photo = poster_image
            except:
                poster = Label(root, text='\n\n\n\n\n\n\n\n\n\n\n\n' +
                                          movie + '\n\n\n\n\n\n\n\n\n\n\n\n',
                               borderwidth=3, relief='ridge')

            poster.pack(in_=movie_frame, side=TOP)

            title = Label(text=info['title'], bg='#363636', fg='white')
            title.pack(in_=movie_frame, side=TOP)

            cast = Label(text='Cast: ' + info['cast'], wraplengt=200, bg='#363636', fg='white')
            cast.pack(in_=movie_frame, side=TOP)

            director = Label(text='Directed by: ' + info['director(s)'], bg='#363636', fg='white')
            director.pack(in_=movie_frame, side=TOP)

            rating = Label(text='Rating: ' + str(info['rating']) + '/10', bg='#363636', fg='white')
            rating.pack(in_=movie_frame, side=TOP)
            synopsis = Label(text='Synopsis: ' + info['synopsis'], wraplengt=200, bg='#363636',
                             fg='white')
            synopsis.pack(in_=movie_frame, side=TOP)

            movie_frame.pack(in_=frame, side=LEFT, padx=20)
            self.recommended_films_frame.append(movie_frame)

    def _update_recommendations(self) -> None:
        """Show the next 5 (at most) recommended films. In other words, remove the films
        that are currently being shown to show the next one. If there are no next ones, a
        warning label is created to say so and nothing is destroyed."""

        if self.recommended_list[5:] == []:
            Label(root, text='No more films to show.').pack(in_=self, side=TOP)
            return

        # remove the films that are currently being shown from the list
        self.recommended_list = self.recommended_list[5:]
        self.recommended_text.destroy()
        self.update_recommendations_button.destroy()
        for movie_frame in self.recommended_films_frame:
            movie_frame.destroy()
        self.recommended_films_frame = []
        self.recommended_frame.destroy()

        # re-initialize the frame, now with the update list
        self.recommended_frame = Frame(root, bg='#363636')
        self._init_recommendations(self)
        self.recommended_frame.pack(in_=self, side=TOP)


if __name__ == '__main__':
    clean_films()

    root = Tk()
    root.title = 'Movie Recommendations'
    root.configure(background='#363636')

    Project()
    root.mainloop()
