import sqlite3
import urllib2
from bs4 import BeautifulSoup
import copy
# and other libraries

class IMDb_crawler():

	# intializing the database
	def __init__(self, dbname):
		self.con = sqlite3.connect(dbname)
		self.c = self.con.cursor()
	
	def __del__(self):
		self.con.close()

	def commit(self):
		self.con.commit()

	def create_tables(self):
		self.c.execute("create table movie_data(name TEXT, imdb_id TEXT, year INT, rating REAL, total_users INT, genres TEXT\
			, summary TEXT)")
		# to make the search faster
		self.c.execute("create index imdb_idx on movie_data(imdb_id)")

	def is_indexed(self, movie_id):
		field = self.c.execute("select * from movie_data where imdb_id= '%s'" % movie_id).fetchone()
		if field:
			return True
		else:
			return False

	def add_to_index(self, movie_data):                 # data is dictionary structure
			self.c.execute("insert into movie_data values(?,?,?,?,?,?,?)", (movie_data['title'], movie_data['movie_id'], 
				movie_data['year'], movie_data['rating'], movie_data['users'], movie_data['genre'], movie_data['summary']))
		

	def crawl(self, limit = 100, min_rating = 5):
		print "how many movies u wanna crawl: "
		limit = input()
		print "crawling...."
		self.create_tables()
		movies_indexed_so_far = 0
		genres = ("action","comedy","mystery","sci_fi","adventure","fantasy","horror","animation","drama","thriller")
		iteration = 0
		count = 0
		while count < limit:
			for genre in genres:
				if count > limit:
					break
				c = self.get_webpage(genre, iteration)
				if c == None:
					continue
				soup = BeautifulSoup(c.read())                        # change to c.read() later on
				data = self.get_movie_data(soup, min_rating)
				for i in range(len(data)):
					if not self.is_indexed(data[i]['movie_id']):
						self.add_to_index(data[i])
						movies_indexed_so_far += 1
				self.commit()
				print "movies_indexed_so_far",movies_indexed_so_far
				count += 50
			iteration += 1


	def get_webpage(self, genre, iteration):
		try:
			self.url = "http://www.imdb.com/search/title?at=0&genres="+genre+"&sort=moviemeter,asc&start="+str(iteration*50+1)+"&title_type=feature"
			c = urllib2.urlopen(self.url)
			return c
		except Exception, e:
			print "error is ",e
			print "could not open url",self.url
			return None


	def get_movie_data(self, soup, min_rating):
	    tr_tag = soup.table.tr 
	    tr_next = tr_tag.next_sibling.next_sibling
	    data = []
	    movie_data = {}
	    while tr_next:
	    	td = tr_next.contents[5]
	    	name = self.get_movie_name(td)
	    	year = self.get_movie_year(td)
	    	movie_id = self.get_movie_id(td)
	    	rating = self.get_movie_rating(td)
	    	users = self.get_movie_users(td)
	    	summary = self.get_movie_summary(td)
	    	genre = self.get_movie_genre(td)
	    	tr_next = tr_next.next_sibling.next_sibling
	    	data.append({'title':name,'year':year,'movie_id':movie_id,'rating':rating,'users':users,'summary':summary,'genre':genre})
	    return data
	    

	def get_movie_name(self, text):
		try:	
			return text.span.next_sibling.next_sibling.string
		except:
			print "check movie name tag in this url",self.url

	def get_movie_rating(self, text):
		div = text.div.div
		if div.has_key('title') and div['title'].split()[0] == 'Users':
			value = div['title']
			return value.split()[3].split('/')[0]
		else:
			return 0

	def get_movie_users(self, text):
		div = text.div.div
		if div.has_key('title') and div['title'].split()[0] == 'Users':
			value = div['title']
			temp = value.split()[4].split('(')[1].split(',')
			return ''.join(temp)
		else:
			return 0

	def get_movie_year(self, text):
		try:
			return text.contents[5].string.split('(')[1].split(')')[0]
		except:
			print "check movie year tag in this url",self.url

	def get_movie_id(self, text):
		try:
			return text.span['data-tconst']
		except:
			print "check movie id tage in this url",self.url

	def get_movie_genre(self, text):
		br = text.br
		try:	
			tag = br.contents[7]
			a = tag.a
			string_of_genre = ""
			while a:
				string_of_genre += a.string
				string_of_genre += ','
				if a.next_sibling:	
					a = a.next_sibling.next_sibling
				else:
				 	break
			return string_of_genre
		except:
			#print "check movie genre in this url",self.url
			return ""

	def get_movie_summary(self, text):
		return text.div.next_sibling.next_sibling.string

	def query(self, q):
		for row in self.c.execute(q):
			print row

crawler = IMDb_crawler('movie_dbase')
crawler.crawl()


