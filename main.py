from typing import Optional, List
from fastapi.encoders import jsonable_encoder
from fastapi.params import Body

import motor.motor_asyncio
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from bson.objectid import ObjectId
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from PyObjectId import PyObjectId
import requests
import urllib
import io
from PIL import Image
from PIL.ExifTags import TAGS
from typing import Dict
import mongod

origins = [
    "http://localhost:8080",
    "https://localhost:8080",
    "https://dm-art.herokuapp.com",
    "http://localhost:4200",
    "http://localhost:3000",
]


# client = motor.motor_asyncio.AsyncIOMotorClient(CONNECTION_STRING)
# print(f"Client obtained as {client}")
# db = client.artworks
# print(f"artworks db is {db}")
# ARTWORK = db.get_collection("works")
# CONFIG = db.get_collection("config")
# print(f"config collection is {CONFIG}")

thumbnail_cache: Dict[str, io.BytesIO] = {}


app = FastAPI(title="dmart")
app.add_event_handler("startup", mongod.connect_db)
app.add_event_handler("shutdown", mongod.close_db)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

class Config(BaseModel):
  imageRootURI: str
  artist: str
  recentWorkYears: Optional[int] = 1
  backgroundColor: Optional[str] = "#FFF8DC"
  navbarTextColor: Optional[str] = "#164D7A"
  navbarHoverTextColor: Optional[str] = "#F97924"
  filename: Optional[str] = 'david_marshall_'

  class Config:
    allow_population_by_field_name = True
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}


class ArtworkBase(BaseModel):
  title: Optional[str]
  price: Optional[float]
  year: Optional[int]
  width: Optional[int]
  height: Optional[int]
  tags: Optional[List[str]]
  categoryName: Optional[str]
  media: Optional[str]
  imagePath: Optional[str]
  isSold: Optional[bool]
  class Config:
    allow_population_by_field_name = True
    arbitrary_types_allowed = True

class Artwork(ArtworkBase):
  id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
  title: str = Field(...)
  class Config:
    allow_population_by_field_name = True
    arbitrary_types_allowed = True
    json_encoders = {ObjectId: str}


@app.get("/")
def read_root():
  return {"Hello": "World"}

@app.get("/config", response_description="config object", response_model=Config)
async def get_config ():
  config = mongod.db.get_collection('config')
  conf = await config.find_one()
  return conf


@app.post("/works",
  status_code=status.HTTP_201_CREATED,
  description="Create an artwork",
  response_model=Artwork)
async def create_work (work: ArtworkBase):
  # input is ArtworkBase (no id) because jsonable_encoder will add in an id without ObjectId wrapper if the work
  # of type Artwork
  work_dict = jsonable_encoder(work) # creates dict ready for insertion into Mongo (no id)
  artworks = mongod.db.get_collection('works')
  insert_result = await artworks.insert_one(work_dict) # _id will be generated
  new_artwork = await artworks.find_one(ObjectId(insert_result.inserted_id))
  # convert dictionary to Artwork object for serialization
  r = Artwork(**new_artwork)
  return r
  

@app.patch("/works/{id}",
  description="Update artwork", 
  status_code=status.HTTP_200_OK,
  response_model=Artwork)
async def update_work (id: str, artwork: ArtworkBase):
  print(f'Update {id} {artwork}')

  artworks = mongod.db.get_collection('works')
  artwork = artwork.dict(exclude_unset=True)
  field_json = jsonable_encoder(artwork)
  if len(artwork) >= 1:
      update_result = await artworks.update_one({"_id": ObjectId(id)}, {"$set": field_json})
      if update_result.modified_count == 1:
          if (
              updated_artwork := await artworks.find_one({"_id": ObjectId(id)})
          ) is not None:
              return updated_artwork
  if (existing_artwork := await artworks.find_one({"_id": ObjectId(id)})) is not None:
      return existing_artwork
  raise HTTPException(status_code=404, detail=f"Artwork {id} not found")

@app.delete("/works/{id}", 
  description="Delete an artwork")
async def delete_work(id: str):
  artworks = mongod.db.get_collection('works')
  delete_result = await artworks.delete_one({"_id": ObjectId(id)})
  if delete_result.deleted_count == 1:
    return Response(status_code=status.HTTP_204_NO_CONTENT)
  else:
    raise HTTPException(status_code=404, detail=f"Artwork {id} not found")


@app.get("/works",
  description="List all works", 
  response_model=List[Artwork])
async def get_all_works():
  artworks = mongod.db.get_collection('works')
  num = await artworks.count_documents({})
  print("There are ", num, "artworks")
  x = await artworks.find().to_list(1000)
  return x

@app.get("/works/tag/{tag}",response_description="List all works with matching tag",
 response_model=List[Artwork])
async def get_works_by_tag(tag: str):
  artworks = mongod.db.get_collection('works')
  results = [w for w in await artworks.find().to_list(1000) if tag in w['tags']]
  count = len(results)
  print(f"Tag match found {count} records ")
  return results

@app.get("/works/{id}",response_description="Get a single work", response_model=Artwork)
async def get_work_by_id(id: str):
  artworks = mongod.db.get_collection('works')
  try:
    if (work := await artworks.find_one({"_id": ObjectId(id)})) is not None:
      return work
  except Exception:
    raise HTTPException(status_code=404, detail=f"Work {id} not found")

@app.get("/works/search/{term}",response_description="Search works",
  response_model=List[Artwork])
async def search_works(term: str):
  artworks = mongod.db.get_collection('works')
  results = [w for w in await artworks.find().to_list(1000) if work_matches(w,term)]
  count = len(results)
  print(f"Search match found {count} records ")
  return results



@app.get('/images/thumbnail',
  response_description="Returns a thumbnail image",
  response_class="StreamingResponse",
  responses= {200: {"description": "an image", "content": {"image/jpeg": {}}}})
async def thumbnail_image (filename: str, isNumber = False):
  # will check for image in cache and fetch it from github and will both cache it and return it.
  config = mongod.db.get_collection('config')
  imgio = thumbnail_cache.get(filename)
  if not imgio:
    config = await config.find_one()

    filename = f'david_marshall_{filename}.jpg' if isNumber else urllib.parse.unquote(filename)
    url = config['imageRootURI'] + "/" + filename
    print("fetching from " + url)
    # get the high-res image from github
    source_img = requests.get(url, stream=True)
    if not source_img.ok:
      raise HTTPException(status_code=404, detail="Could not find github image: " + url)
    image = Image.open(source_img.raw)
    image = convert_to_thumbnail(image)
    imgio = io.BytesIO()
    image.save(imgio, 'JPEG')
    # cache the thumbnail
    thumbnail_cache[filename] = imgio
  imgio.seek(0)
  return StreamingResponse(content=imgio, media_type="image/jpeg")

def convert_to_thumbnail (img: Image):
  # print(img._getexif().items())
  if img._getexif():
    exif=dict((TAGS[k], v) for k, v in img._getexif().items() if k in TAGS)
    # some images have meta-data (Exif) that contains info like orientation.
    if orient:=exif.get('Orientation'):
        # only handles 2 of 8 possible orientations
        if orient == 8:
          img = img.rotate(90, expand=True)
        elif orient == 2:
          img = img.rotate(270, expand=True)

  img.thumbnail((100,100), Image.ANTIALIAS)
  return img


def work_matches (work, term):
  term = term.lower()
  for key in ['title', 'price', 'year', 'width', 'height', 'media', 'tags']:
    if term in str(work.get(key,'')).lower():
      return True
  return False




