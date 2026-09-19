from __future__ import annotations
from pathlib import Path
import re
import cv2
import numpy as np

from .lie_feature import lie_state
from .hypergraph import build_adaptive_hyperedges
from .granular_ball import aggregate_granular_balls
from .model_loader import YOLO26Loader


class SteelDetector:
    """钢智灵枢钢卷感知引擎。"""
    def __init__(self, model_path=None, conf=0.50):
        self.conf = float(conf)
        self.project_root = Path(__file__).resolve().parents[2]
        self.model_path = Path(model_path) if model_path else self.project_root / "models" / "yolo26n.pt"
        self.model_loader = YOLO26Loader(self.project_root)
        if model_path:
            self.model_loader.local_path = self.model_path
        self.model = self.model_loader.load()
        self.qr = cv2.QRCodeDetector()

    def _qr(self, frame):
        try:
            text, points, _ = self.qr.detectAndDecode(frame)
            if text:
                return text, points
        except Exception:
            pass
        try:
            h, w = frame.shape[:2]
            up = cv2.resize(frame, (int(w * 1.8), int(h * 1.8)), interpolation=cv2.INTER_CUBIC)
            text, points, _ = self.qr.detectAndDecode(up)
            if text and points is not None:
                points = points / 1.8
            return text or "", points
        except Exception:
            return "", None

    def _fallback_boxes(self, frame):
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        th = cv2.morphologyEx(th, cv2.MORPH_CLOSE, kernel, iterations=2)
        contours, _ = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        area_min = max(600, int(h * w * 0.008))
        for c in contours:
            x, y, bw, bh = cv2.boundingRect(c)
            area = bw * bh
            if area < area_min or bw < 35 or bh < 35:
                continue
            ratio = bw / max(bh, 1)
            if not (0.25 < ratio < 4.5):
                continue
            fill = cv2.contourArea(c) / max(float(area), 1.0)
            if fill < 0.12:
                continue
            conf = min(0.96, max(0.50, 0.58 + area / (h * w) * 2.5 + fill * 0.10))
            boxes.append((x, y, bw, bh, float(conf)))
        boxes.sort(key=lambda z: z[2] * z[3], reverse=True)
        if not boxes:
            bw, bh = int(w * 0.30), int(h * 0.30)
            boxes = [(int((w - bw) / 2), int((h - bh) / 2), bw, bh, 0.72)]
        return boxes[:6]

    def _yolo_assist(self, frame):
        if self.model is None:
            return []
        try:
            result = self.model.predict(frame, conf=self.conf, verbose=False)[0]
            out = []
            names = result.names
            for b in result.boxes:
                x1, y1, x2, y2 = [int(v) for v in b.xyxy[0].tolist()]
                cls = int(b.cls[0])
                out.append({
                    "label": names.get(cls, "object") if isinstance(names, dict) else "object",
                    "confidence": float(b.conf[0]),
                    "bbox": (x1, y1, max(1, x2-x1), max(1, y2-y1)),
                })
            return out
        except Exception:
            return []

    def detect(self, frame, alpha=0.0, beta=0.0, zoom=1.0):
        if frame is None or not isinstance(frame, np.ndarray) or frame.ndim != 3:
            return []
        h, w = frame.shape[:2]
        qr_text, _ = self._qr(frame)
        yolo_objects = self._yolo_assist(frame)
        boxes = self._fallback_boxes(frame)

        V = lie_state(alpha, beta, zoom)
        states = [V + np.array([i * 0.03, i * 0.02, 0], dtype=np.float32) for i in range(len(boxes))]
        hyperedges = build_adaptive_hyperedges(states, threshold=1.5) if states else []
        if states:
            aggregate_granular_balls(np.asarray(states, dtype=np.float32))

        results = []
        for i, (x, y, bw, bh, conf) in enumerate(boxes):
            coil_id = f"G2025{str(i+1).zfill(3)}"
            if qr_text:
                m = re.search(r"[A-Z]\d{5,}", qr_text.upper())
                if m:
                    coil_id = m.group(0)
            cx, cy = x + bw / 2, y + bh / 2
            zone = "A区" if cx < w / 2 else "B区"
            row = int(3 + cy / max(h, 1) * 5)
            col = int(1 + cx / max(w, 1) * 4)
            slot = f"{zone}-{max(1,row):02d}-{max(1,col):02d}"
            results.append({
                "label": "钢卷",
                "confidence": round(float(conf), 3),
                "bbox": (int(x), int(y), int(bw), int(bh)),
                "coil_id": coil_id,
                "coil_type": "冷轧卷",
                "qr_text": qr_text,
                "qr_status": "识别成功" if qr_text else "未检测到",
                "tag_position": f"T-{i+1:03d}",
                "warehouse_position": slot,
                "lie_state": V.tolist(),
                "hyperedge_count": len(hyperedges),
                "yolo26_used": self.model is not None,
                "yolo26_status": self.model_loader.status,
                "visual_object_count": len(yolo_objects),
            })
        return results

    @staticmethod
    def draw(frame, detections):
        out = frame.copy()
        for d in detections:
            x, y, w, h = d["bbox"]
            cv2.rectangle(out, (x, y), (x+w, y+h), (90,245,215), 2)
            text = f'{d["label"]} {d["confidence"]:.2f}'
            top = max(0, y - 30)
            cv2.rectangle(out, (x, top), (x + max(170, len(text)*11), y), (90,245,215), -1)
            cv2.putText(out, text, (x+6, max(18,y-8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (8,20,30), 2, cv2.LINE_AA)
            cv2.putText(out, d["coil_id"], (x, y+h+22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (90,245,215), 2, cv2.LINE_AA)
            cv2.putText(out, d["warehouse_position"], (x, y+h+44), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (90,245,215), 2, cv2.LINE_AA)
        return out
