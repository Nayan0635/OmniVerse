from core.rag import answer

print("🤖 Type 'exit' to quit.")
while True:
    q = input("\nAsk? ")
    if q.lower() == "exit":
        print("Agent: Cya! 👋")
        break
    print("\nAgent: ")
    print(answer(q))