from __future__ import annotations
from pathlib import Path


class YOLO26Loader:
    """Load local YOLO26n or let Ultralytics obtain the official checkpoint."""
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.local_path = self.project_root / "models" / "yolo26n.pt"
        self.model = None
        self.status = "未加载"

    def load(self):
        try:
            from ultralytics import YOLO
        except Exception as exc:
            self.status = f"Ultralytics不可用: {exc}"
            return None
        try:
            # Prefer the submitted local checkpoint. If absent, Ultralytics may download
            # the official checkpoint when internet access is available.
            source = str(self.local_path) if self.local_path.exists() else "yolo26n.pt"
            self.model = YOLO(source)
            self.status = f"YOLO26n已加载: {source}"
        except Exception as exc:
            self.model = None
            self.status = f"YOLO26n加载失败: {exc}"
        return self.model
