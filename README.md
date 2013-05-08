Imdb-crawler
============
A crawler meant for creating movie database.It extracts the information about the movies from the IMDb websie.
Why go on Imdb and search for movies individually when you can query your offline database the way you want,like
1) get all movies of 2013 having rating more than 8.
2) get top 10 movies(on the basis of rating) having more than 200,000 users.

Contents:
==========
The repo contains a source file 'imdb_crawler.py' and a sqlite database file 'movie_dbase' created on 5-5-13 with
12473 unique entries.

Usage:
==========
Before running the source file you need to install BeautifulSoup (parser) and sqlite3. For more information about
the above two libraries visit:
1) http://www.crummy.com/software/BeautifulSoup/
2) http://www.sqlite.org/

Now, run imdb_crawler.py in python shell
then program will ask you to input the number of movies you want to crawl.
Now sit back and relax......

your database will be stored in a file called movie_dbase.Each entry contains the info about movies' ratings,
genre,brief summary and other relevant data.

if you know sql you can query the sqlite framework. For example

1) select movie_name from movie_data where rating > 7 and rating < 8 and users > 50000
2) select movie_name,summary from movie_data where rating > 8 and year == 2013

