from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_delivery():
    return "Got delivery"