from pymongo import MongoClient
CONNECTION_STRING="mongodb+srv://marshall62:t0mand3rs@dm-art-cluster.6xsvm.mongodb.net/test?authSource=admin&replicaSet=atlas-10ss2z-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true"
client = MongoClient(CONNECTION_STRING)
db = client['artworks']
ARTWORK = db.get_collection("works")


def printall () :
  for w in ARTWORK.find():
    print(w)
  print("There are ", ARTWORK.count_documents({}), "works")
