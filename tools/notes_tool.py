from tools.base import BaseTool, ToolResult
from tools.registry import register_tool
import memory.database as db
import datetime

@register_tool
class NotesPlugin(BaseTool):
    @property
    def name(self) -> str:
        return "notes"

    @property
    def description(self) -> str:
        return "Saves, reads, lists, and manages user notes in the database."

    def execute(self, action: str = "create", title: str = "Note", content: str = "", note_id: int = 0, **kwargs) -> ToolResult:
        act = action.strip().lower()
        try:
            if act == "create":
                ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO user_notes (title, content, created_at) VALUES (?, ?, ?)",
                        (title, content, ts)
                    )
                    inserted_id = cursor.lastrowid
                return ToolResult(success=True, result=str(inserted_id))
            elif act == "read":
                n_id = note_id or kwargs.get("id") or title
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, title, content FROM user_notes WHERE id = ? OR title = ?", (str(n_id), str(n_id)))
                    row = cursor.fetchone()
                if row:
                    r = dict(row)
                    return ToolResult(success=True, result=f"Note ID {r['id']}: {r['title']}\nContent: {r['content']}")
                return ToolResult(success=False, result=f"Note '{n_id}' not found.")
            else:
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, title FROM user_notes ORDER BY id DESC LIMIT 10")
                    rows = cursor.fetchall()
                notes_list = [f"ID {r['id']}: {r['title']}" for r in rows]
                return ToolResult(success=True, result=f"Notes: {', '.join(notes_list) if notes_list else 'No notes yet.'}")
        except Exception as e:
            return ToolResult(success=False, result=str(e))

    def validate(self, result: ToolResult) -> bool:
        return result.success

    def rollback(self, **kwargs) -> ToolResult:
        note_id = kwargs.get("note_id")
        if note_id:
            with db.get_connection() as conn:
                conn.execute("DELETE FROM user_notes WHERE id = ?", (note_id,))
            return ToolResult(success=True, result=f"Deleted note ID {note_id} during rollback.")
        return ToolResult(success=True, result="No notes rollback required.")

    def status(self) -> str:
        return "ACTIVE"
