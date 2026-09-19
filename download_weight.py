from pathlib import Path
from ultralytics import YOLO

root = Path(__file__).resolve().parent
out = root / "models" / "yolo26n.pt"
model = YOLO("yolo26n.pt")
source = Path("yolo26n.pt")
if source.exists() and source.resolve() != out.resolve():
    out.write_bytes(source.read_bytes())
print(f"YOLO26n ready: {out}")
