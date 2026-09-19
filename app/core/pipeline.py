from __future__ import annotations
from pathlib import Path
import cv2

from app.perception.steel_detector import SteelDetector
from app.digital_twin.state import DigitalTwin
from app.scheduling.scheduler import SmartCraneScheduler


class SteelHubPipeline:
    def __init__(self):
        self.detector = SteelDetector()
        self.twin = DigitalTwin()
        self.scheduler = SmartCraneScheduler(3)

    def process_frame(self, frame, alpha=0.0, beta=0.0, zoom=1.0):
        detections = self.detector.detect(frame, alpha, beta, zoom)
        for d in detections:
            self.twin.update_coil(d)
        return detections, self.detector.draw(frame, detections)

    def create_tasks(self, detections):
        tasks = []
        for i, d in enumerate(detections):
            tasks.append({
                "task_id": f"TASK-{i+1:03d}",
                "coil_id": d["coil_id"],
                "source": d["warehouse_position"],
                "target": "B区-05-03" if i == 0 else f"C区-04-{i+1:02d}",
                "priority": "高" if i == 0 else "普通",
                "status": "待命",
            })
        return self.scheduler.schedule(tasks)

    def process_image(self, path):
        frame = cv2.imread(str(path))
        if frame is None:
            raise FileNotFoundError(path)
        return self.process_frame(frame)

    def process_video(self, path, callback=None, max_frames=0):
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            raise RuntimeError(f"无法打开视频: {path}")
        index = 0
        last = None
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            detections, drawn = self.process_frame(frame)
            last = (detections, drawn)
            if callback:
                callback(index, frame, drawn, detections)
            index += 1
            if max_frames and index >= max_frames:
                break
        cap.release()
        return last
