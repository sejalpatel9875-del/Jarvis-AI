"""
commercial/backups.py
~~~~~~~~~~~~~~~~~~~~~
Automated Backup Manager & Disaster Recovery Engine for JARVIS AI OS.
"""

import time
import os
import zipfile
import uuid
from typing import Dict, List, Any


class BackupManager:
    """Manages database snapshots, vector store backups, and disaster recovery health."""

    def __init__(self):
        self.backup_history: List[Dict[str, Any]] = []

    def create_backup(self, backup_type: str = "FULL") -> Dict[str, Any]:
        """Creates a timestamped backup snapshot of SQLite databases, vector stores, and memory facts."""
        start_time = time.time()
        backup_id = f"bak_{uuid.uuid4().hex[:8]}_{int(time.time())}"
        backup_dir = os.path.join(".", "logs", "backups")
        os.makedirs(backup_dir, exist_ok=True)

        backup_file = os.path.join(backup_dir, f"{backup_id}.zip")

        try:
            # Create a ZIP archive containing critical database & config files
            with zipfile.ZipFile(backup_file, "w", zipfile.ZIP_DEFLATED) as zipf:
                # Add SQLite databases if present
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if (
                            file.endswith(".db")
                            or file.endswith(".sqlite")
                            or file == "mcp_servers.json"
                        ):
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, arcname=os.path.relpath(file_path, "."))

            duration_ms = round((time.time() - start_time) * 1000, 2)
            file_size_bytes = os.path.getsize(backup_file) if os.path.exists(backup_file) else 0

            record = {
                "backup_id": backup_id,
                "type": backup_type,
                "file_path": backup_file,
                "size_bytes": file_size_bytes,
                "created_at": int(time.time()),
                "duration_ms": duration_ms,
                "status": "SUCCESS",
            }
            self.backup_history.append(record)

            return {"success": True, "backup": record}
        except Exception as ex:
            record = {
                "backup_id": backup_id,
                "type": backup_type,
                "error": str(ex),
                "created_at": int(time.time()),
                "status": "FAILED",
            }
            self.backup_history.append(record)
            return {"success": False, "error": str(ex)}

    def get_disaster_recovery_status(self) -> Dict[str, Any]:
        """Evaluates disaster recovery health, RPO (Recovery Point Objective), and RTO targets."""
        last_success = None
        for b in reversed(self.backup_history):
            if b["status"] == "SUCCESS":
                last_success = b
                break

        rpo_minutes = 0.0
        if last_success:
            rpo_minutes = round((time.time() - last_success["created_at"]) / 60.0, 1)

        return {
            "disaster_recovery_status": "HEALTHY" if last_success else "WARNING",
            "last_backup_id": last_success["backup_id"] if last_success else None,
            "last_backup_time": last_success["created_at"] if last_success else None,
            "current_rpo_minutes": rpo_minutes,
            "target_rpo_minutes": 60.0,
            "target_rto_minutes": 15.0,
            "total_backups_count": len(self.backup_history),
        }


# Singleton Instance
backup_manager = BackupManager()
