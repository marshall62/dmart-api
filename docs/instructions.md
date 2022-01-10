## Running
Be in dmart root and source .venv/bin/activate
cd api
uvicorn main:app --reload

## Debugging the python API with VSCode

Needed to create a .venv python virtual environment at the project dir root

I then created a Fast API run/debug config .vscode/launch.json 

I wasn't successful at getting VSCode to use my venv that lived in /api/venv.
So its best to create the venv at the project root with 
python -m venv .venv  
and then vscode automatically detects it and offers to set it as the default for the project.

## Image strategy

I'm using an endpoint /images/thumbnail?filename=<pathToFile_or_number>&isNumber=true/false to fetch images.
If a pathTofilename is passed, we go to the github repo and look for it (this can accept paths now).  If a number is passed (requiring the isNumber=true) then we translate it to a filename like "david_marshall_<number>.jpg" and look it up in github.

I'm thinking that the numbering scheme is probably not a good idea and I should stick with using the URL.

The endpoint fetches the high-res image from github and returns a thumbnail that works within an HTML <img>.  The endpoint caches these thumbnails in memory so that it will be faster after the first time.  

I created a utility that standardizes the naming of all my image files.  Images live in the directory /images .  The utility is /api/rename_images.py .  Running it will take all the files in the images directory and standardize their names to be 
david_marshall_XXX.jpg where XXX is an incremented number.   The utility preserves files that have been previously renamed and will only tamper with newly added images.  

## Website Update strategy

My goal for updating the website has this most common work flow:

Use: Add some new paintings:

  1. Add the high-res images to the /images folder
  1. run the rename_images utility  (and note what the files are renamed to)
  1. push the images to github 
  1. [TODO] add records to mongo db in MongoAtlas that point to these files in github.
  1. that's it.

I see that MongoAtlas has a read/write data API that allows me to modify the database from a locally running client (using curl for example).  This will make it relatively easy to create a utility that I can use to put new records into mongo from my machine.  See [https://docs.atlas.mongodb.com/api/data-api/]

## Heroku:

On git push this should deploy on heroku automatically

https://dmart-api.herokuapp.com
https://dmart-api.herokuapp.com/config



