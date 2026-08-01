import datetime
import json
import re
from typing import Dict, Any, List, Optional
from services.llm_router import ask_ai
from tools.registry import tool_registry
from tools.base import ToolResult
from services.calendar_reminders import calendar_reminders
from services.lead_ai_assistant import lead_ai_assistant
from memory.manager import _default_manager

class AdvancedAIEngine:
    """
    Advanced AI Capabilities Engine for Jarvis AI OS.
    Implements Task Planning, Multi-step reasoning, Document analysis,
    OCR & Image understanding, Meeting summaries, AI Notes, Smart reminders,
    Knowledge retrieval, and context-aware Voice commands.
    """

    # 1. Task Planning & Multi-step reasoning
    def plan_and_reason(self, goal: str) -> Dict[str, Any]:
        """Orchestrates multi-step reasoning plan execution for a user goal."""
        from services.workflow_execution import workflow_execution
        res = workflow_execution.execute_workflow("adhoc_run", {"goal": goal})
        return {
            "success": res.get("success", False),
            "goal": goal,
            "status": res.get("status"),
            "progress": res.get("progress"),
            "results": res.get("results"),
            "duration_ms": res.get("duration_ms")
        }

    # 2. Document Analysis
    def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Reads document and extracts structured summaries, highlights, action items, and issues."""
        res = tool_registry.execute("file_manager", action="read", path=file_path)
        if not res.success:
            return {"success": False, "error": res.result}

        prompt = (
            f"Analyze the following document content in detail. Generate a JSON response with keys:\n"
            f"- 'summary': Executive summary of the text\n"
            f"- 'highlights': List of key highlights\n"
            f"- 'action_items': List of action items identified\n"
            f"- 'issues': List of problems/risks identified.\n\n"
            f"Content:\n{res.result[:5000]}"
        )
        reply = ask_ai(prompt)
        reply_clean = re.sub(r'```json|```', '', reply).strip()
        try:
            data = json.loads(reply_clean)
            return {"success": True, "file_path": file_path, **data}
        except Exception:
            return {"success": True, "file_path": file_path, "raw_summary": reply}

    # 3. OCR & Image Understanding
    def understand_image(self, image_path: str, user_prompt: str = "Describe what you see in the image.") -> Dict[str, Any]:
        """Performs mock OCR screen scan and builds semantic analysis context of image contents."""
        ocr_res = tool_registry.execute("ocr", image_path=image_path)
        
        prompt = (
            f"You are the visual brain of Jarvis. The user wants to understand an image. "
            f"OCR results extracted from the image: '{ocr_res.result}'. "
            f"User request: '{user_prompt}'. "
            f"Provide a detailed semantic analysis of what this image represents and answer the user query."
        )
        reply = ask_ai(prompt)
        return {
            "success": True,
            "image_path": image_path,
            "ocr_text": ocr_res.result,
            "analysis": reply
        }

    # 4. Meeting Summaries
    def summarize_meeting(self, transcript: str) -> Dict[str, Any]:
        """Summarizes transcription into minutes containing highlights, action items, and key decisions."""
        res = lead_ai_assistant.generate_meeting_notes(lead_id=1, raw_transcript=transcript)
        return {
            "success": True,
            "summary": res.get("summary", "Summary details"),
            "action_items": res.get("action_items", []),
            "key_decisions": res.get("key_decisions", [])
        }

    # 5. AI Notes
    def create_ai_note(self, title: str, content: str) -> Dict[str, Any]:
        """Summarizes note text, extracts tags, and inserts into note database and long-term memory."""
        prompt = (
            f"Given the note content, generate a concise summary and a list of 3-5 keywords/tags for indexing.\n"
            f"Format as JSON with keys: 'summary' and 'tags' (list).\n\n"
            f"Content:\n{content}"
        )
        reply = ask_ai(prompt)
        reply_clean = re.sub(r'```json|```', '', reply).strip()
        try:
            data = json.loads(reply_clean)
        except Exception:
            data = {"summary": content[:100], "tags": ["general"]}

        tags_str = ", ".join(data.get("tags", []))
        formatted_title = f"{title} (AI Tags: {tags_str})"
        
        # Save note
        res = tool_registry.execute("notes", action="create", title=formatted_title, content=content)
        
        # Save summary to long term memory
        _default_manager.save_long_term_fact(title, data.get("summary", ""))

        return {
            "success": res.success,
            "note_title": formatted_title,
            "summary": data.get("summary"),
            "tags": data.get("tags")
        }

    # 6. Smart Reminders
    def parse_and_create_reminder(self, text: str) -> Dict[str, Any]:
        """Extracts task details and dates from natural language to create calendar reminders."""
        now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = (
            f"Given the user request, parse out the task/reminder title and the target due date/time.\n"
            f"Format as JSON with keys: 'title' (str) and 'due_at' (str in YYYY-MM-DD HH:MM:SS format, assume current local time is {now_ts}).\n\n"
            f"Request: '{text}'"
        )
        reply = ask_ai(prompt)
        reply_clean = re.sub(r'```json|```', '', reply).strip()
        try:
            data = json.loads(reply_clean)
        except Exception:
            data = {"title": text, "due_at": ""}

        res = calendar_reminders.create_reminder("default", data.get("title", "Reminder"), data.get("due_at", ""))
        return {
            "success": res.get("success", False),
            "parsed_title": data.get("title"),
            "parsed_due_at": data.get("due_at"),
            "reminder": res.get("reminder")
        }

    # 7. Knowledge Retrieval
    def retrieve_knowledge(self, query: str) -> Dict[str, Any]:
        """Performs semantic lookup over RAG chunks and long-term memory abstracts."""
        facts = _default_manager.semantic_search_knowledge(query, limit=3)
        ltm = _default_manager.semantic_search_long_term(query, limit=2)
        return {
            "success": True,
            "query": query,
            "knowledge_facts": facts,
            "long_term_memories": ltm
        }

    # 8. Voice Commands & Context Awareness
    def execute_voice_command(self, voice_text: str) -> Dict[str, Any]:
        """Interprets spoken commands context-awarely utilizing recent turns."""
        recent_turns = _default_manager.get_recent(limit=3)
        context = "\n".join([f"User: {t.user_message}\nJarvis: {t.assistant_reply}" for t in recent_turns])

        prompt = (
            f"Conversation Context:\n{context}\n\n"
            f"User Spoken Command: '{voice_text}'\n\n"
            f"Formulate a context-aware Hinglish voice response addressing this command."
        )
        reply = ask_ai(prompt)
        return {
            "success": True,
            "command": voice_text,
            "voice_response": reply
        }

# Global Singleton Engine
advanced_ai = AdvancedAIEngine()
