"""
Purpose:
LLM-Powered Goal Analyzer and Step Reasoning Engine for Jarvis Planner System.

Responsibilities:
- Analyze user goals into capability-abstracted execution plans
- Generate ordered PlanStep instances with capability requirements (no hardcoded tool names)
- Establish step dependencies (depends_on) and confidence scores
- Provide fast-path casual plans for simple queries

Dependencies:
- agents/state.py
- services/llm_router.py
- tools/registry.py
"""

import json
import re
from typing import List, Dict, Any, Optional
from agents.state import PlanModel, PlanStep, StepStatus, PlanStatus, Capability
from services.llm_router import ask_ai
from tools.registry import tool_registry

class ReasonerEngine:
    """
    Goal Analyzer & Reasoning Engine.
    Generates capability-abstracted PlanModels.
    """
    def __init__(self):
        pass

    def get_available_capabilities(self) -> List[str]:
        """Queries ToolRegistry to return list of active capabilities."""
        tools = tool_registry.list_tools()
        capabilities = set()
        for t in tools:
            name = t["name"].lower()
            if name == "calculator":
                capabilities.add(Capability.MATH.value)
            elif name == "search":
                capabilities.add(Capability.WEB_SEARCH.value)
            elif name == "browser":
                capabilities.add(Capability.WEB_SCRAPE.value)
            elif name == "system":
                capabilities.add(Capability.SYSTEM_CONTROL.value)
            elif name == "music":
                capabilities.add(Capability.MUSIC_PLAYBACK.value)
        return list(capabilities)

    def is_casual_query(self, goal: str) -> bool:
        """Determines if the goal is a casual single-turn query."""
        text = goal.strip().lower()
        words = text.split()
        if len(words) <= 5 and not any(kw in text for kw in ["search", "download", "calculate", "open", "play", "scrape", "write"]):
            return True
        return False

    def generate_plan(self, user_goal: str, memory_context: str = "") -> PlanModel:
        """
        Analyzes user goal and constructs a structured PlanModel.
        Uses rule-based capability extraction and LLM reasoning.
        """
        goal_text = user_goal.strip()
        goal_lower = goal_text.lower()
        
        # 1. Fast Path for Casual Queries
        if self.is_casual_query(goal_text):
            step = PlanStep(
                step_number=1,
                description=f"Respond to user query: '{goal_text}'",
                capability="llm_casual",
                confidence=1.0,
                estimated_latency=0.3
            )
            return PlanModel(goal=goal_text, steps=[step])

        steps: List[PlanStep] = []

        # 2. Rule-Based & Semantic Capability Parsing
        # Math detection
        if re.search(r'\b(\d+[\+\-\*\/\%]\d+|\d+\s*\%|\bcalculate\b)', goal_lower):
            steps.append(
                PlanStep(
                    step_number=len(steps) + 1,
                    description=f"Evaluate math expression: {goal_text}",
                    capability=Capability.MATH.value,
                    args={"expression": goal_text},
                    confidence=0.98,
                    estimated_latency=0.005
                )
            )

        # Music detection
        elif "play" in goal_lower and ("song" in goal_lower or "music" in goal_lower or "youtube" in goal_lower):
            song_name = re.sub(r'^(open\s+youtube\s+and\s+)?play\s+(song\s+)?', '', goal_lower, flags=re.IGNORECASE).strip()
            steps.append(
                PlanStep(
                    step_number=len(steps) + 1,
                    description=f"Play song '{song_name}' on YouTube",
                    capability=Capability.MUSIC_PLAYBACK.value,
                    args={"song_name": song_name},
                    confidence=0.95,
                    estimated_latency=1.0
                )
            )

        # Search detection
        elif any(kw in goal_lower for kw in ["search", "google", "find", "look up"]):
            query = re.sub(r'^(search|google|find|look up)\s+(for\s+)?', '', goal_lower, flags=re.IGNORECASE).strip()
            steps.append(
                PlanStep(
                    step_number=1,
                    description=f"Search web for '{query}'",
                    capability=Capability.WEB_SEARCH.value,
                    args={"query": query},
                    confidence=0.95,
                    estimated_latency=1.5
                )
            )
            # Add web scrape / summary step dependent on Step 1 if user requested summary
            if any(kw in goal_lower for kw in ["summarize", "points", "details"]):
                steps.append(
                    PlanStep(
                        step_number=2,
                        description="Extract and summarize search results",
                        capability=Capability.WEB_SCRAPE.value,
                        args={"query": query},
                        depends_on=[1],
                        confidence=0.90,
                        estimated_latency=2.0
                    )
                )

        # Default: Single LLM Reasoning Step
        if not steps:
            steps.append(
                PlanStep(
                    step_number=1,
                    description=f"Process goal with AI reasoning: '{goal_text}'",
                    capability="llm_general",
                    args={"prompt": goal_text},
                    confidence=0.90,
                    estimated_latency=0.8
                )
            )

        return PlanModel(goal=goal_text, steps=steps)

# Global Reasoner Engine Instance
default_reasoner = ReasonerEngine()
