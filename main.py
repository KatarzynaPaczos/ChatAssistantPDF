def main():
    print("Hello from fastapi!")


if __name__ == "__main__":
    main()

    import uvicorn
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000, reload=True)
