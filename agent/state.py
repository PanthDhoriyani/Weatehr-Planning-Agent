from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
import operator

# AgentState is basically the "memory" of our agent
# every node in the graph reads from this and writes back to this
# the 'messages' list keeps growing as the agent takes more steps

class AgentState(TypedDict):
    # operator.add means new messages get ADDED to the list (not replaced)
    messages: Annotated[list[BaseMessage], operator.add]
