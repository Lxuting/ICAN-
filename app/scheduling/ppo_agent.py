from __future__ import annotations
import random


class PPOAgent:
    """PPO-compatible decision interface.

    This software release provides a deterministic inference policy for the demo.
    A trained policy checkpoint can be plugged in later without changing the UI/API.
    """
    def __init__(self, crane_count=3):
        self.crane_count = crane_count
        self.policy_path = None

    def select_crane(self, task, loads):
        available = [i for i in range(self.crane_count) if i not in task.get("blocked_cranes", [])]
        if not available:
            available = list(range(self.crane_count))
        return min(available, key=lambda i: loads.get(i, 0))
