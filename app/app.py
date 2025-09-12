from fastapi import FastAPI, Body

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True}

@app.put("/")
def update_item(data: dict = Body(...)):
    return {"received": data}
    