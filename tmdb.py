# API KEY = 5843a33b560b93bc80c1cb21f4faac1b

def get_movie_data(title):

    movie_dict = {}  # making an empty dictionary so we can put the movie info in it

    # building the URL using the title the user put in
    url = f"http://www.omdbapi.com/?apikey=1846eeb9&t={title}&plot=full"

    try:
        # trying to get the data from the API and turn it into a dictionary
        movie_dict = requests.get(url).json()
        return movie_dict  # if it works, give the dictionary back

    except:
        # if something goes wrong then I just mark it as fail
        movie_dict['Title'] = {'fail'}
        return movie_dict


def movie_data():
    # ask the user what movie they want info for
    movie = input("Please insert a movie: ")

    # call the function that grabs the API data
    movie_data = get_movie_data(movie)

    # check if it was successful
    if not movie_data['Title'] == 'fail':
        keylist = movie_data.keys()

        # loop through every part of the data and print
        for key in keylist:
            print(f"{key} is {movie_data[key]}")  # showing key/value pairs in readable way

        return movie_data  # give the data back in case we want to use it later

    else:
        # if the movie wasn't valid
        print('That is not a valid film. Please try again.')
        return ""  # returning an empty so nothing breaks

def list_of_movies():
    collecting_movies = True  # using this to keep the loop running
    movie_list = []  # this is where I'm gonna store all the movie data

    while collecting_movies == True:
        # ask the user for movies one at a time
        addmovie = input('Add a movie here, or enter quit to stop : ')
        if addmovie.lower() == 'quit':
            collecting_movies = False  # stop asking for movies
            break

        # get the data for that movie from the API
        film_data = get_movie_data(addmovie)

        # if it didn't fail, then add it to list
        if not film_data['Title'] == 'fail':
            movie_list.append(film_data)

    sorted_list = []

    for movie in movie_list:
        var = (movie['Metascore'])  # access the Metascore
        sorted_list.append(var)

    sorted_list.sort(reverse=True)  # sort movies from highest score to lowest

    final_list = []

    for elem in sorted_list:
        for comparison in movie_list:
            # if the score matches, then that’s the correct movie
            if comparison['Metascore'] == elem:
                filmtitle = comparison['Title']
        final_list.append((filmtitle, elem))  # add it as a tuple

    print("The ordered list of movies and Metascore ratings:")
    for i in final_list:  # just print each one
        print(i)

    return final_list  # gives the sorted through list back


def movie_genres():
    movie_list = []  # empty list to store movie data later

    while True:
        # ask the user what movie they want to add
        addmovie = input("Add a movie here, or enter quit to stop: ")
        if addmovie.lower() == "quit":
            break  # leave the loop if they are done

        while True:
            # try to get data for the movie they typed
            filmData = get_movie_data(addmovie)


            if filmData.get('Response') == 'True':
                movie_list.append(filmData)  # save the movie data
                break  # move on to the next movie
            else:
                addmovie = input("Movie not found. Try a different movie, or enter quit to stop: ")
                if addmovie.lower() == "quit":
                    break  # leave this loop and go to main loop
        if addmovie.lower() == "quit":
            break  # fully exit if they typed quit

    genre_list = []  # list for genres

    # go through the movies we saved
    for movie in movie_list:
        if "Genre" in movie:
            # .split makes it so we get each genre on its own
            genres = movie["Genre"].split(", ")
            for g in genres:
                # this makes sure we don’t get duplicates
                if g not in genre_list:
                    genre_list.append(g)

    return genre_list  # final list of all genres used

import requests
from PIL import Image
from io import BytesIO
from IPython.display import display

def display_movie_poster():
    # asking the user what movie they want the poster for
    movie_title = (input("Please input the movie name: "))

    api_key = "1846eeb9"

    # building the url so it matches the exact format this API wants
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"

    # sending the request to the API
    response = requests.get(url)

    # turning the response into a dictionary so I can grab things like Title and Poster
    data = response.json()

    # checking if the movie was found (if Response is True then it worked)
    if data["Response"] == "True":
        poster_url = data["Poster"]  # getting the url of the poster

        print("Movie:", data["Title"])  # printing title
        print("Year:", data["Year"])    # printing year
        print("Poster URL:", poster_url)  # the actual poster link

        # now I go and actually get the image from that poster link
        poster_response = requests.get(poster_url)

        # converting it into something python can show
        img = Image.open(BytesIO(poster_response.content))

        # displays the poster in the output cell instead of popping up randomly
        display(img)
    else:
        # if the movie name didn’t work
        print("Try a different movie.")

    # giving back the poster url if I want to use it for something else later
    return poster_url

# LARGE DISCLAIMER
# YES WE DID A MOVIE API PROJECT PREVIOUSLY IN THIS CLASS
# THIS IS A DIFFERENT API THAT JUST HAPPENS TO ALSO BE ABOUT MOVIES
# IT WAS THE BEST ONE WE FOUND
# WE HAD TO CODE THE WHOLE THING IT IS A DIFFERENT API WITH DIFFERENT KEYS AND URLS ETC
# THANK YOU FOR YOUR TIME

API_KEY = "1846eeb9"

import requests
from PIL import Image
from io import BytesIO
from IPython.display import display  # to show image in the output cell

# function to show a movie poster
def display_movie_poster(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data["Response"] == "True":
        poster_url = data["Poster"]
        print("Movie:", data["Title"])
        print("Year:", data["Year"])
        print("Poster URL:", poster_url)

        poster_response = requests.get(poster_url)
        img = Image.open(BytesIO(poster_response.content))
        display(img)  # shows in the cell
    else:
        print("Movie not found. Try a different title.")

# main loop
running = True

while running:
    print("\n")
    print("This program has several movie-related functions.")
    print("Please input the number for what you want to do, or type 'quit' to stop.")
    print("1 - list data relevant to a single movie title")
    print("2 - input a list of movies and order them by rating")
    print("3 - input a list of movies and compile a list of all the genres involved")
    print("4 - input a movie and its poster will be displayed")
    print("\n")

    op_type = input("Input number here: ")

    # let them quit
    if op_type.lower() == "quit":
        running = False
        break

    # make sure they typed a number
    if not op_type.isdigit():
        print("Please enter 1, 2, 3, or 4 (or 'quit').")
        continue

    op_type = int(op_type)

    if op_type == 1:
        filmData = movie_data()

    elif op_type == 2:
        filmData = list_of_movies()

    elif op_type == 3:
        filmData = movie_genres()
        print(filmData)

    elif op_type == 4:
        movie_title = input("Enter the title of the movie you want the poster for: ")
        display_movie_poster(movie_title)

    else:
        print("That is not a valid option. Please choose 1, 2, 3, or 4.")




