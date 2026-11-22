from agent.graph import build_graph
from agent.memory import get_farm_profile
from langchain_core.messages import HumanMessage


def main():
    print("=" * 60)
    print("   🌾  AgriShield AI — Precision Agriculture Sentinel  🌾")
    print("=" * 60)
    profile = get_farm_profile()
    print(f"Active Farm: {profile.get('location')} | Crop: {profile.get('crop')} ({profile.get('growth_stage')})")
    print("Ask any agronomic question (irrigation, spraying, pests, harvesting).")
    print("Type 'quit' or 'q' to exit.\n")

    # Compile the LangGraph graph
    app = build_graph()

    while True:
        try:
            user_input = input("👨‍🌾 Farmer: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting AgriShield AI.")
            break

        if user_input.lower() in ["quit", "exit", "q"]:
            print("Exiting AgriShield AI. Happy Farming! 🌾")
            break

        if not user_input:
            continue

        print("\n🤔 AgriShield agents coordinating telemetry and risk audit...\n")

        result = app.invoke({
            "messages": [HumanMessage(content=user_input)],
            "crop_name": profile.get("crop", "Cotton"),
            "growth_stage": profile.get("growth_stage", "Flowering"),
            "farm_location": profile.get("location", "Pune"),
            "active_agent": None,
            "memory_context": None,
            "weather_data": None,
            "threat_level": None,
            "critic_notes": None,
        })

        final_answer = result["messages"][-1].content
        agent_used = result.get("active_agent", "Agent")
        threat = result.get("threat_level", "MODERATE")

        print(f"[{agent_used.upper()} | THREAT: {threat}]")
        print(final_answer)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()
