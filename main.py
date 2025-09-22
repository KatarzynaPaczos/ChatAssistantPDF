import uvicorn  # noqa: B008

from app.llm import chat_once


def generate_chat(user_text: str) -> str:
    # in cli only one session_id = "cli"
    return chat_once("cli",  user_text)


def open_chat():
    print("AI assistant with the history (Ctrl+C to exit)")
    try:
        while True:
            q = input("\nYou: ")
            a = generate_chat(q)
            print(f"\nAssistant: {a}")
    except KeyboardInterrupt:
        print("\nSee you soon!")


if __name__ == "__main__":
    # open_chat()  # how to organize it better (parser) + more extentions not only pdf
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000, reload=True)
