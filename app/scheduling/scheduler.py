from __future__ import annotations
from .ppo_agent import PPOAgent


class SmartCraneScheduler:
    def __init__(self, crane_count=3):
        self.agent = PPOAgent(crane_count)
        self.crane_count = crane_count

    def schedule(self, tasks):
        loads = {i: 0 for i in range(self.crane_count)}
        result = []
        for task in tasks:
            crane = self.agent.select_crane(task, loads)
            loads[crane] += 1
            result.append({
                **task,
                "crane": f"天车{crane+1}",
                "status": task.get("status", "待命"),
                "route": f'{task.get("coil_id", "G2025001")} → {task.get("target", "B区-05-03")}',
            })
        return result
