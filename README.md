# Major Project (Locale Estimation on Social Media)
This is a Web App that developed using Django. It uses technologies such as DataMining and Information Retrieval to compute on various text data on tweets.

The project includes two main parts:
	
	1. Web Application
		This is a web information system that implemented by Django and It never utilized the ORM that provided by Django as there is lots of Spatial Data. It's easier to use SQL query to manipulate data.
		In this case, 'model.py' is never touched and instead, 'db.py' file was created as a layer to communicated between the application and database.	
	2. Data Crawler
		This is a simple console application that only used to crawl tweets from Twitter Stream API. Once it runs, it continuesly extracting data from the API and push collected data into database after refined. Both two parts share the same database.

Data Storage

	Postgres with PostGIS extention, which controls all the spatial data.
