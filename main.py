from agent.graph import build_graph
from langchain_core.messages import HumanMessage


def main():
    print("=" * 45)
    print("      🌧️  Weather Planning Agent  🌧️")
    print("=" * 45)
    print("Ask me anything about weather!")
    print("Type 'quit' to exit.\n")

    # build the langgraph agent
    app = build_graph()

    while True:
        user_input = input("You: ").strip()

        # exit condition
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye! Stay dry! ☂️")
            break

        # skip empty input
        if not user_input:
            continue

        print("\n🤔 Agent is thinking...\n")

        # invoke the agent with the user's question
        result = app.invoke({
            "messages": [HumanMessage(content=user_input)]
        })

        # the last message in the list is always the final answer
        final_answer = result["messages"][-1].content

        print(f"Agent: {final_answer}")
        print("\n" + "-" * 45 + "\n")


if __name__ == "__main__":
    main()
