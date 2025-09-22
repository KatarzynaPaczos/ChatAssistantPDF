import argparse

import uvicorn

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


def main():
    parser = argparse.ArgumentParser(description="Run Chat Assistant")
    parser.add_argument(
        "mode",
        choices=["api", "cli"],
        help="Run in 'api' mode (FastAPI with uvicorn) or 'cli' mode (terminal chat)",
    )
    args = parser.parse_args()

    if args.mode == "cli":
        open_chat()
    elif args.mode == "api":
        uvicorn.run("app.api:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == "__main__":
    main()
    # todo:  add more extentions not only pdf
    # error handling when couldn't read the file
    # tests
