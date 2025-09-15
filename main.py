from app.llm import chat_once, get_history
import uvicorn

def generate_chat(user_text: str) -> str:
    #if yu use 'cli' - it is one session
    hist = get_history("cli")
    return chat_once(hist, user_text)


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
    #open_chat()
    uvicorn.run("app.app:app", host="127.0.0.1", port=8000, reload=True)
