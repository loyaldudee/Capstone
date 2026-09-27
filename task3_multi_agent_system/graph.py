"""
LangGraph Multi-Agent Workflow for Claims Intelligence & Investigation
----------------------------------------------------------------------
Implements the 5-agent collaborative workflow using official LangGraph:
- Parallel Fan-Out: Retrieval, Risk Analysis, and Anomaly Detection agents.
- Fan-In: Summarization Agent synthesizes consolidated case brief.
- Conditional Edge / A2A Handoff: Escalates suspicious/complex claims to Investigation Support Agent.
- Human-in-the-Loop decision gate.
"""

import os
import sys
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from task3_multi_agent_system.state import ClaimsInvestigationState, create_initial_state
from task3_multi_agent_system.agents.retrieval_agent import claims_retrieval_agent_node
from task3_multi_agent_system.agents.risk_analysis_agent import claims_risk_analysis_agent_node
from task3_multi_agent_system.agents.anomaly_agent import anomaly_detection_agent_node
from task3_multi_agent_system.agents.summarization_agent import claims_summarization_agent_node
from task3_multi_agent_system.agents.investigation_agent import investigation_support_agent_node


def route_handoff(state: ClaimsInvestigationState) -> Literal["investigate", "routine_finish"]:
    """
    Conditional Edge Evaluator:
    Determines whether a claim is routine or triggers an A2A handoff to Investigation Support.
    """
    if state.get("requires_investigation_handoff", False):
        return "investigate"
    return "routine_finish"


def build_claims_multi_agent_graph():
    """Builds and compiles the StateGraph workflow."""
    workflow = StateGraph(ClaimsInvestigationState)

    # 1. Register the 5 Agent Nodes
    workflow.add_node("retrieval_agent", claims_retrieval_agent_node)
    workflow.add_node("risk_analysis_agent", claims_risk_analysis_agent_node)
    workflow.add_node("anomaly_detection_agent", anomaly_detection_agent_node)
    workflow.add_node("summarization_agent", claims_summarization_agent_node)
    workflow.add_node("investigation_support_agent", investigation_support_agent_node)

    # 2. Parallel Fan-Out: Specialists run concurrently from START
    workflow.add_edge(START, "retrieval_agent")
    workflow.add_edge(START, "risk_analysis_agent")
    workflow.add_edge(START, "anomaly_detection_agent")

    # 3. Fan-In: Consolidate specialist outputs into Summarization Agent
    workflow.add_edge("retrieval_agent", "summarization_agent")
    workflow.add_edge("risk_analysis_agent", "summarization_agent")
    workflow.add_edge("anomaly_detection_agent", "summarization_agent")

    # 4. Conditional Edge: Dynamic Agent Handoff
    workflow.add_conditional_edges(
        "summarization_agent",
        route_handoff,
        {
            "investigate": "investigation_support_agent",
            "routine_finish": END
        }
    )

    # 5. Investigation Support completes the workflow
    workflow.add_edge("investigation_support_agent", END)

    # Compile the graph
    app = workflow.compile()
    return app


# Global compiled workflow instance
claims_agent_app = build_claims_multi_agent_graph()


def run_claims_investigation(claim_data: Dict[str, Any], customer_profile: Dict[str, Any] = None) -> ClaimsInvestigationState:
    """
    Entrypoint function to run a full multi-agent investigation on any claim dictionary.
    Can be imported and called by FastAPI server, test scripts, or UI.
    """
    initial_state = create_initial_state(claim_data, customer_profile)
    final_state = claims_agent_app.invoke(initial_state)
    return final_state


if __name__ == "__main__":
    # Test print Mermaid representation of the graph
    try:
        mermaid_graph = claims_agent_app.get_graph().draw_mermaid()
        print("LangGraph Mermaid Architecture Representation:")
        print(mermaid_graph)
    except Exception as e:
        print(f"Workflow compiled successfully. ({e})")
