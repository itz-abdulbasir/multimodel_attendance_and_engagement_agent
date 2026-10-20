"""
Multimodal Attendance & Engagement Agent - Storage Layer
Manages Generated Audio Files, Generated Code Files, Uploaded Files, and Local Storage exports.
"""

import os
import shutil
from typing import List, Dict, Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
AUDIO_DIR = os.path.join(STORAGE_DIR, "audio")
CODE_DIR = os.path.join(STORAGE_DIR, "code")
UPLOADS_DIR = os.path.join(STORAGE_DIR, "uploads")
ATTENDANCE_DIR = os.path.join(STORAGE_DIR, "attendance")

for d in [STORAGE_DIR, AUDIO_DIR, CODE_DIR, UPLOADS_DIR, ATTENDANCE_DIR]:
    os.makedirs(d, exist_ok=True)

class StorageManager:
    @staticmethod
    def list_generated_audio_files() -> List[Dict[str, Any]]:
        files = []
        for f in os.listdir(AUDIO_DIR):
            if f.endswith((".wav", ".mp3")):
                path = os.path.join(AUDIO_DIR, f)
                files.append({
                    "name": f,
                    "size_bytes": os.path.getsize(path),
                    "url": f"/storage/audio/{f}",
                    "created_at": os.path.getctime(path)
                })
        return sorted(files, key=lambda x: x["created_at"], reverse=True)

    @staticmethod
    def list_generated_code_files() -> List[Dict[str, Any]]:
        files = []
        for f in os.listdir(CODE_DIR):
            if f.endswith((".py", ".json", ".txt")):
                path = os.path.join(CODE_DIR, f)
                with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                    content = fp.read()
                files.append({
                    "name": f,
                    "size_bytes": os.path.getsize(path),
                    "content": content,
                    "created_at": os.path.getctime(path)
                })
        return sorted(files, key=lambda x: x["created_at"], reverse=True)

    @staticmethod
    def list_uploaded_files() -> List[Dict[str, Any]]:
        files = []
        for f in os.listdir(UPLOADS_DIR):
            path = os.path.join(UPLOADS_DIR, f)
            files.append({
                "name": f,
                "size_bytes": os.path.getsize(path),
                "url": f"/storage/uploads/{f}",
                "created_at": os.path.getctime(path)
            })
        return sorted(files, key=lambda x: x["created_at"], reverse=True)

    @staticmethod
    def save_upload(filename: str, content_bytes: bytes) -> str:
        safe_name = os.path.basename(filename)
        dest_path = os.path.join(UPLOADS_DIR, safe_name)
        with open(dest_path, "wb") as f:
            f.write(content_bytes)
        return dest_path
