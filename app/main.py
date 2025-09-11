from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"ok": True}

'''
def main():
    print("Welcome on the PDF assistant page!")


if __name__ == "__main__":
    main()
    import uvicorn
    uvicorn.run()
'''