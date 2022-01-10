from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:4200",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

@app.get("/")
def read_root():
  return {"Hello": "World"}
