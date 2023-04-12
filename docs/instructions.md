## Mongo Db

An environment var must be set to provide the URL to the cloud
mongo db.  The environment var is MONGO_DATASOURCE

Db connection string can be obtained here:
https://cloud.mongodb.com/v2/615490640c90e4261e121d89#clusters/detail/dm-art-cluster

It is also in my serve.sh (which is not in github)

Click the Connect button and select Mongo Db Compass.  It will show the connection string.

Load the dmart.postman_collection.json into Postman for testing API either 
running locally or in Heroku

## Running


Be in dmart-api root and source venv/bin/activate

set MONGO_DATASOURCE environment var and run
uvicorn main:app --reload

OR

./serve.sh   will do the above.

## Troubleshooting Mongo DB 

Load the dmart.postman_collection.json into Postman for testing API

I'm using cloud.mongodb.com and login with my google id.

When running my local API it sometimes fails to connect to the mongodb.
Here is background info:

Line 41 of main.py is a callback that connects to mongodb when fastapi launches.

Test the function that connects (mongod.connect_db):
 - venv/bin/activate
 - export MONGO_DATASOURCE=<value>
 - python3
 - import mongod
 - mongod.test_query()
 - Expect to see that it shows the configuration object

Make sure the MONGO_DATASOURCE environment variable is correctly set to the above URI
(when running in PyCharm it should be set in the run/debug config)

Launch MongoDB Compass Desktop App and Connect Using the URI above (it's saved)
View the artworks collection


## Debugging the python API with VSCode

Needed to create a .venv python virtual environment at the project dir root

I then created a Fast API run/debug config .vscode/launch.json 

I wasn't successful at getting VSCode to use my venv that lived in /api/venv.
So its best to create the venv at the project root with 
python3 -m venv venv  
vscode automatically detects a .venv it and offers to set it as the default for the project.  If I name it venv, then I manually set it by clicking the footer and adding the path to it as ./venv/bin/python

## Image strategy

I'm using an endpoint /images/thumbnail?filename=<pathToFile_or_number>&isNumber=true/false to fetch images.
If a pathTofilename is passed, we go to the github repo and look for it (this can accept paths now).  If a number is passed (requiring the isNumber=true) then we translate it to a filename like "david_marshall_<number>.jpg" and look it up in github.

I'm thinking that the numbering scheme is probably not a good idea and I should stick with using the URL.

The endpoint fetches the high-res image from github and returns a thumbnail that works within an HTML <img>.  The endpoint caches these thumbnails in memory so that it will be faster after the first time.  

I created a utility that standardizes the naming of all my image files.  Images live in the directory /images .  The utility is /rename_images.py .  Running it will take all the files in the images directory and standardize their names to be 
david_marshall_XXX.jpg where XXX is an incremented number.   The utility preserves files that have been previously renamed and will only tamper with newly added images.  

## Website Update strategy

My goal for updating the website has this most common work flow:

Use: Add some new paintings:

  1. Add the high-res images to the /images folder
  1. run the rename_images utility  (and note what the files are renamed to)
  1. push the images to github 
  1. [TODO build a tool] add records to mongo db in MongoAtlas that point to these files in github.
  1. that's it.

I see that MongoAtlas has a read/write data API that allows me to modify the database from a locally running client (using curl for example).  This will make it relatively easy to create a utility that I can use to put new records into mongo from my machine.  See [https://docs.atlas.mongodb.com/api/data-api/]

## Heroku:

Note:  I have to use a Google free authentication app on my phone to login to Heroku

On git push this should deploy on heroku automatically

It was necessary to put my connection to mongo in separate methods that are called by
fastapi.  See mongod.py and use of db.get_collection within main.py.   

https://dmart-api.herokuapp.com
https://dmart-api.herokuapp.com/config



