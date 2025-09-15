# Chat Assistand PDF

This project is a backend application built with FastAPI that enables users to ask questions in natural language. The system integrates a Large Language Model (LLM), which generates responses based on private documents such as PDFs, notes, and scientific articles. The goal is to provide an intelligent, document-aware question–answering interface.

To run the application you must type:
```python
uv run python main.py
```
To see the results go to:
http://localhost:8000 or
http://localhost:8000/docs


It is possible to use it with docker also - you must have docker installed:
```python
docker --version
```
To start docker container run - build the image and then run the container
```python
uv export --frozen --no-dev --no-cache -o requirements.txt
docker build -t chat-assistant-pdf .
docker run -p 8000:8000 chat-assistant-pdf
```
Now instead of all this commands above you can run:
```python
docker compose up --build
```