import datetime as dt
from collections import defaultdict


class User:
    def __init__(self, id):
        """
        Initialize a user with an id, a dictionary of ratings, a dictionary of dates, and a count of the number of movies watched
        """
        self.id = id #user id
        self.ratings = defaultdict(float) #movie_id: rating given by user
        self.dates = defaultdict(dt.datetime) #movie_id: date rating was given
        self.n_watched = 0 #number of movies watched by user

    def add_rating(self, movie, rating: int, date: str):
        """
        Add a rating to the user's ratings and add the user to the movie's watched_by list
        """
        self.ratings[movie.id] = rating #add rating to user's ratings
        self.dates[movie.id] = date #add date to user's dates
        movie.add_user(self) #add user to movie's watched_by list
        self.n_watched += 1
    
    def normalize_ratings(self):
        """
        Normalize the user's ratings by subtracting the average rating and dividing by the standard deviation
        """
        avg_rating = self.average_rating()
        sd_rating = self.sd_rating()
        for movie_id in self.ratings:
            self.ratings[movie_id] -= avg_rating
            self.ratings[movie_id] /= sd_rating

    def get_ratings(self):
        """
        Return a list of ratings given by the user
        """
        return list(self.ratings.values())

    def average_rating(self):
        """
        return the average rating given by the user
        """
        return sum(self.get_ratings())/len(self.ratings)

    def sd_rating(self):
        """
        return the standard deviation of the user's ratings
        """
        avg_rating = self.average_rating()
        sd = (sum([(rating - avg_rating)**2 for rating in self.get_ratings()])/len(self.ratings))**0.5
        return sd if sd != 0 else 1
    
    def __str__(self):
        return f"User {self.id} has rated {self.n_watched} movies"
    
    def __repr__(self):
        return f"User {self.id} has rated {self.n_watched} movies"
    
    def __getitem__(self, movie_id: str):
        return self.ratings[movie_id]
    

class Movie:
    def __init__(self, id, title, year):
        self.id = id #movie id
        self.title = title #movie title 
        self.year = year #movie release year
        self.users = defaultdict(User) #list of users who have watched the movie
        self.n_watched = 0
    
    def add_user(self, user: User):
        """
        add a user who has watched the movie
        """
        self.users[user.id] = user
        self.n_watched += 1

    def get_ratings(self):
        """
        Return a list of ratings given to the movie by users
        """
        return [user.ratings[self.id] for user in self.users.values()]
    
    def __str__(self):
        return f"{self.title}, {self.year}"
    
    def __repr__(self):
        return f"Movie({self.id}, {self.title}, {self.year}) seen by {self.n_watched} users"
    
    def __getitem__(self, user_id: str):
        return self.users[user_id]
    