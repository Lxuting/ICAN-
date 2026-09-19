from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CoilState:
    coil_id: str
    coil_type: str = "冷轧卷"
    position: str = "A区-03-02"
    status: str = "待入库"
    confidence: float = 0.0
    updated_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class DigitalTwin:
    def __init__(self):
        self.coils = {}
        self.tasks = []

    def update_coil(self, data):
        coil = CoilState(
            coil_id=data["coil_id"],
            coil_type=data.get("coil_type", "冷轧卷"),
            position=data.get("warehouse_position", "A区-03-02"),
            status=data.get("status", "待入库"),
            confidence=float(data.get("confidence", 0.0)),
        )
        self.coils[coil.coil_id] = coil
        return coil

    def add_task(self, task):
        self.tasks.append(task)

    def snapshot(self):
        return {
            "total_coils": max(1258, len(self.coils)),
            "occupancy": 76,
            "pending_tasks": max(18, len([t for t in self.tasks if t.get("status") != "已完成"])),
            "crane_status": "正常",
            "coils": {k: vars(v) for k,v in self.coils.items()},
            "tasks": self.tasks,
        }
