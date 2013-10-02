from pymongo import MongoClient
import urllib2
from bs4 import BeautifulSoup
import copy
import sys
import time
# and other libraries

class IMDb_crawler():

	# intializing the database
	def __init__(self, dbname, collection):
		self.client = MongoClient('localhost',27017)
		self.db = self.client[dbname]
		self.set = self.db[collection]
	
	def __del__(self):
		pass

	def create_indexes(self):                       # not needed for mongodb
		# to make the search faster
		self.c.execute("create index if not exists imdb_idx on movie_data(imdb_id)")

	def is_indexed(self, _id, count):
		if self.set.find_one({'_id':_id}):
			return True
		else:
			self.movies_indexed_so_far += 1
			sys.stdout.write("\rAfter scrapping %d movies, movies_indexed_so_far %d" %(count + 50, self.movies_indexed_so_far))
			return False


	def add_to_index(self, movie_data):                 # data is dictionary structure
			self.set.insert(movie_data)
		

	def crawl(self, limit = 100, min_rating = 5):
		print "how many movies u wanna crawl: "
		limit = input()
		print "crawling...."
		#self.create_tables()
		self.movies_indexed_so_far = 0
		so_far = 0
		dots = 0
		# total 7 genres, many genres overlap so no need to define all genres here
		genres = ("action","comedy","mystery","adventure","horror","drama","thriller")
		iteration = 103
		count = 0
		while count < limit:
			for genre in genres:
				if count >= limit:
					break
				c = self.get_webpage(genre, iteration)
				if c == None:
					continue
				if so_far == self.movies_indexed_so_far:
					sys.stdout.write("\rAfter scrapping %d movies, movies_indexed_so_far %d" %(count + 50, self.movies_indexed_so_far))
					for dot in range(dots%5):
						sys.stdout.write(".")
					dots += 1
					sys.stdout.write("    ")
				soup = BeautifulSoup(c.read())                      
				data = self.get_movie_data(soup, min_rating)
				for i in range(len(data)):
					if not self.is_indexed(data[i]['_id'], count):
						self.add_to_index(data[i])
					else:
						pass                                 # here add waiting animation
				#self.commit()
				#print "movies_indexed_so_far",movies_indexed_so_far
				count += 50
			iteration += 1
		sys.stdout.write("\n")


	def get_webpage(self, genre, iteration):
		try:
			self.url = "http://www.imdb.com/search/title?at=0&genres="+genre+"&sort=num_votes&start="+str(iteration*50+1)+"&title_type=feature"
			c = urllib2.urlopen(self.url)
			#sys.stdout.write("\rpage fetched")
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
	    	_id = self.get_movie_id(td)
	    	rating = self.get_movie_rating(td)
	    	users = self.get_movie_users(td)
	    	summary = self.get_movie_summary(td)
	    	genre = self.get_movie_genre(td)
	    	tr_next = tr_next.next_sibling.next_sibling
	    	data.append({'title':name,'year':year,'_id':_id,'rating':rating,'users':users,'summary':summary,'genre':genre})
	    return data
	    

	def get_movie_name(self, text):
		try:	
			return text.span.next_sibling.next_sibling.string
		except:
			print text.span.next_sibling.string
			print "check movie name tag in this url",self.url

	def get_movie_rating(self, text):
		div = text.div.div
		if div.has_attr('title') and div['title'].split()[0] == 'Users':
			value = div['title']
			return float(value.split()[3].split('/')[0])
		else:
			return 0

	def get_movie_users(self, text):
		div = text.div.div
		if div.has_attr('title') and div['title'].split()[0] == 'Users':
			value = div['title']
			temp = value.split()[4].split('(')[1].split(',')
			return int(''.join(temp))
		else:
			return -1

	def get_movie_year(self, text):
		try:
			return int(text.contents[5].string.split('(')[1].split(')')[0])
		except:
			print "check movie year tag in this url",self.url
			return 0

	def get_movie_id(self, text):
		try:
			return text.span['data-tconst']
		except:
			print "check movie id tag in this url",self.url
			return 'unknown'

	def get_movie_genre(self, text):
		br = text.br
		try:	
			tag = br.contents[7]
			a = tag.a
			list_of_genre = []
			while a:
				list_of_genre.append(a.string)
				if a.next_sibling:	
					a = a.next_sibling.next_sibling
				else:
				 	break
			return list_of_genre
		except:
			print "check movie genre in this url",self.url
			return []

	def get_movie_summary(self, text):
		try:
			return text.div.next_sibling.next_sibling.string
		except:
			return ""

	def query(self, q):
		for row in self.c.execute(q):
			print row

crawler = IMDb_crawler('mdb','set')
crawler.crawl()

