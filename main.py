from flask import Flask,render_template,request,session,redirect,flash,get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from datetime import timedelta
import json
from numpy.core.fromnumeric import transpose
import pandas as pd
import numpy as np
import ast
import random

with open("config.json","r") as c:
    params=json.load(c)["params"]

app=Flask(__name__)
app.secret_key = "secret-key"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI']= params['local_uri']
db=SQLAlchemy(app)


movies_df=pd.read_excel("Movies50.xlsx")

##Movies
Movies={}
num_movies=49
for i in range(num_movies):
    Movies[movies_df.iloc[i,6]]=i

##Genres
Genres=["Action","Adventure","Fantasy","Science Fiction","Crime","Thriller","Animation","Family","Western","Comedy","Drama","Romance","Horror"]
num_genres=len(Genres)

##movie_genres
movie_genres=[]
for i in range(num_movies): 
    temp=[]
    for j in range(num_genres):
        temp.append(0)
    movie_genres.append(temp)

for i in range(num_movies):
    temp=movies_df.iloc[i,1].split('"')
    j=0
    for gen in Genres:
        if gen in temp:
            movie_genres[i][j]=1
        j+=1

    movie_genres=np.array(movie_genres)
class Movies(db.Model):
    Movie_Id=db.Column(db.Integer,primary_key=True)
    budget= db.Column(db.String(50),nullable=False)
    genres= db.Column(db.String(50),nullable=False)
    homepage= db.Column(db.String(50),nullable=False)
    id=db.Column(db.Integer)
    original_language= db.Column(db.String(50),nullable=False)
    original_title= db.Column(db.String(50),nullable=False)
    overview= db.Column(db.String(400),nullable=False)
    img_url= db.Column(db.String(400),nullable=False)
    popularity=db.Column(db.Integer)
    runtime= db.Column(db.String(50),nullable=False)
    tagline= db.Column(db.String(50),nullable=False)
    vote_average= db.Column(db.String(50),nullable=False)
    User1=db.Column(db.String(5))
    reccomend=db.Column(db.Integer)
    User_Rating=db.Column(db.Integer)

    def __init__(self,User1,reccomend,budget,genres,homepage,id,original_language,original_title,overview,img_url,popularity,runtime,tagline,vote_average,User_Rating):
        self.User1=User1
        self.reccomend=reccomend
        self.budget=budget
        self.genres=genres
        self.homepage=homepage
        self.id=id
        self.original_language=original_language
        self.original_title=original_title
        self.overview=overview
        self.img_url=img_url
        self.popularity=popularity
        self.runtime=runtime
        self.tagline=tagline
        self.vote_average=vote_average
        self.User_Rating=User_Rating
        

    

@app.route("/")
def Home():
    p_movie=Movies.query.order_by(desc(Movies.popularity)).limit(6).all()

    movie=Movies.query.filter_by().all()
    ##Users
    Users=['imdb','tmdb','Ayush']
    num_users=len(Users)

    ##user_movies
    user_movies=[]
    user1=[]
    user2=[]
    user3=[]
    for i in range(1,50):
        movie=Movies.query.filter_by(Movie_Id=i).first()
        user3.append(movie.User1)
    for j in range(num_movies):
        user1.append(int(movies_df.iloc[j,18]))
    for j in range(num_movies):
        user2.append((int(movies_df.iloc[j,13]))/20)
    user_movies.append(user1)
    user_movies.append(user2)
    user_movies.append(user3)
    user_movies=np.array(user_movies)


    ##user_genres
    user_genre=np.dot(user_movies,movie_genres)
    user_genre=user_genre/(num_users*10)

    ##user_rating
    user_rating=np.dot(user_genre,transpose(movie_genres))
    for i in range(1,50):
        movie=Movies.query.filter_by(Movie_Id=i).first()
        movie.User_Rating=user_rating[2][i-1]
    r_movie=Movies.query.filter_by(reccomend=1).order_by(desc(Movies.User_Rating)).limit(6).all()

    t_movie=Movies.query.order_by(desc(Movies.vote_average)).limit(6).all()
    return render_template('index.html',params=params,p_movie=p_movie,r_movie=r_movie,t_movie=t_movie)

# @app.route("/genre")
# def Genre():
#     return render_template('genre.html',params=params)

@app.route("/popular")
def Popular():
    movie=Movies.query.order_by(desc(Movies.popularity)).limit(16).all()
    return render_template('popular.html',params=params,movie=movie)

@app.route("/movie/<string:movie_slug>",methods = ['GET','POST'])
def movie_route(movie_slug):
    movie=Movies.query.filter_by(id=movie_slug).first()
    g_list=ast.literal_eval(movie.genres)
    genre_list=[]
    for g in g_list:
        genre_dict=ast.literal_eval(str(g))
        genre_list.append(genre_dict["name"])

    if request.method=='POST':
        movie=Movies.query.filter_by(id=movie_slug).first()
        Rating=request.form.get('rating')
        print(request.form.get('rating'))
        movie.User1=Rating
        movie.reccomend=0
        db.session.commit()
        return redirect('/')
    return render_template('movie.html',params=params,movie=movie,genre=genre_list)

@app.route("/dashboard",methods = ['GET','POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        return render_template('dashboard.html',params=params)
    error = None
    if request.method=='POST':
        username=request.form.get('uname')
        password=request.form.get('password')

        if username==params["admin_user"] and password==params['admin_password']:
            session['user']=username
            flash(params['login_success_msg'])
            return render_template('dashboard.html',params=params)
        else:
            error=params['login_err_msg']
            return render_template('login.html',params=params,error=error)
    
    
        
    return render_template('login.html',params=params)

@app.route("/add",methods = ['GET','POST'])
def add():
    if 'user' in session and session['user'] == params['admin_user']:
        if(request.method=='POST'):
            Title=request.form.get('Title')
            Budget=request.form.get('Budget')
            Genres=request.form.get('Genres')
            Homepage=request.form.get('Homepage')
            Overview=request.form.get('Overview')
            Img=request.form.get('Img')
            Runtime=request.form.get('Runtme')
            Tagline=request.form.get('Tagline')
            Vote=request.form.get('Vote')
            
            movie=Movies(User1=0,reccomend=1,budget=Budget,genres=Genres,homepage=Homepage,id=random.randint(300000,400000),original_language="en",original_title=Title,overview=Overview,img_url=Img,popularity=random.randint(100,150),runtime=Runtime,tagline=Tagline,vote_average=Vote,User_Rating=0)
            db.session.add(movie)
            db.session.commit()
        return render_template('add.html',params=params)
    return render_template('login.html',params=params)

@app.route("/view")
def view():
    if 'user' in session and session['user'] == params['admin_user']:
        movie2=Movies.query.filter_by().all()
        return render_template('view.html',params=params,movie=movie2)
    return render_template('login.html',params=params)
    

@app.before_request
def make_session_permanent():
    session.permanent=True
    app.permanent_session_lifetime=timedelta(minutes=15)

@app.route('/logout')
def logout():
    session.pop('user')
    flash("Logged out Successfully!","success")
    return redirect('/dashboard')


@app.route("/reccomendations")
def Reccomendation():
    movie=Movies.query.filter_by().all()
    ##Users
    Users=['imdb','tmdb','Ayush']
    num_users=len(Users)

    ##user_movies
    user_movies=[]
    user1=[]
    user2=[]
    user3=[]
    for i in range(1,50):
        movie=Movies.query.filter_by(Movie_Id=i).first()
        user3.append(movie.User1)
    for j in range(num_movies):
        user1.append(int(movies_df.iloc[j,18]))
    for j in range(num_movies):
        user2.append((int(movies_df.iloc[j,13]))/20)
    user_movies.append(user1)
    user_movies.append(user2)
    user_movies.append(user3)
    user_movies=np.array(user_movies)


    ##user_genres
    user_genre=np.dot(user_movies,movie_genres)
    user_genre=user_genre/(num_users*10)

    ##user_rating
    user_rating=np.dot(user_genre,transpose(movie_genres))
    for i in range(1,50):
        movie=Movies.query.filter_by(Movie_Id=i).first()
        movie.User_Rating=user_rating[2][i-1]
    movie=Movies.query.filter_by(reccomend=1).order_by(desc(Movies.User_Rating)).limit(params['num_reccomendations']).all()
    return render_template('reccomendation.html',params=params,movie=movie)





app.run(debug=True)