from __future__ import annotations
from pathlib import Path
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QStackedWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QProgressBar, QFrame
)
from app.core.pipeline import SteelHubPipeline
from .theme import MAIN_STYLE


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("钢智灵枢 · 多模态AI钢铁仓储平台")
        self.resize(1280, 820)
        self.setStyleSheet(MAIN_STYLE)
        self.pipeline = SteelHubPipeline()
        self.current_detections = []
        self.video = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_video_frame)
        self.build_ui()

    def build_ui(self):
        root = QWidget(); outer = QVBoxLayout(root)
        header = QHBoxLayout()
        title = QLabel("钢智灵枢"); title.setObjectName("title")
        header.addWidget(title); header.addStretch()
        for text, slot in [("导入图片", self.open_image), ("导入视频", self.open_video), ("创建任务", self.create_task), ("智能调度", self.schedule), ("清空", self.clear_all)]:
            b = QPushButton(text); b.clicked.connect(slot); header.addWidget(b)
        outer.addLayout(header)
        self.stack = QStackedWidget()
        outer.addWidget(self.stack, 1)
        self.setCentralWidget(root)
        self.stack.addWidget(self.dashboard_page())
        self.stack.addWidget(self.recognition_page())
        self.stack.addWidget(self.task_page())
        self.stack.addWidget(self.anomaly_page())

    def card(self):
        f = QFrame(); f.setObjectName("card"); return f

    def dashboard_page(self):
        page = QWidget(); lay = QVBoxLayout(page)
        s = QLabel("查看仓储状态"); s.setObjectName("section"); lay.addWidget(s)
        row = QHBoxLayout()
        for title, value in [("钢卷总数","1258"),("仓储占用率","76%"),("待处理任务","18"),("天车状态","正常")]:
            c=self.card(); cl=QVBoxLayout(c); a=QLabel(title); v=QLabel(value); v.setStyleSheet("font-size:26px;font-weight:700;color:#63e6be;"); cl.addWidget(a); cl.addWidget(v); row.addWidget(c)
        lay.addLayout(row)
        info=QLabel("AI闭环：感知 → 分析 → 决策 → 执行 → 反馈 → 状态更新")
        info.setStyleSheet("font-size:18px;padding:25px;")
        lay.addWidget(info); lay.addStretch(); return page

    def recognition_page(self):
        page=QWidget(); lay=QVBoxLayout(page)
        s=QLabel("钢卷AI识别"); s.setObjectName("section"); lay.addWidget(s)
        row=QHBoxLayout(); self.image_label=QLabel("等待输入图像或视频"); self.image_label.setAlignment(Qt.AlignCenter); self.image_label.setMinimumSize(760,500); self.image_label.setStyleSheet("background:#07101d;border:1px solid #263957;"); row.addWidget(self.image_label,2)
        self.info=QLabel("识别结果将在此显示"); self.info.setAlignment(Qt.AlignTop); self.info.setWordWrap(True); self.info.setStyleSheet("padding:20px;font-size:16px;"); row.addWidget(self.info,1)
        lay.addLayout(row); return page

    def task_page(self):
        page=QWidget(); lay=QVBoxLayout(page); s=QLabel("智能调度与执行状态"); s.setObjectName("section"); lay.addWidget(s)
        self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["任务","钢卷","天车","目标库位","状态"]); lay.addWidget(self.table)
        self.progress=QProgressBar(); self.progress.setValue(60); lay.addWidget(self.progress); return page

    def anomaly_page(self):
        page=QWidget(); lay=QVBoxLayout(page); s=QLabel("异常监测与智能决策"); s.setObjectName("section"); lay.addWidget(s)
        lay.addWidget(QLabel("• 低置信度识别：进入人工确认流程\n• 天车路径冲突：触发调度重规划\n• 库位异常：更新数字孪生状态并生成提示")); lay.addStretch(); return page

    def show_frame(self, frame, detections):
        rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB); h,w,ch=rgb.shape
        q=QImage(rgb.data,w,h,ch*w,QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(q).scaled(self.image_label.size(),Qt.KeepAspectRatio,Qt.SmoothTransformation))
        self.current_detections=detections
        if detections:
            d=detections[0]
            self.info.setText(f"钢卷ID：{d['coil_id']}\n类型：{d['coil_type']}\n标签：{d['tag_position']}\n二维码：{d['qr_status']}\n识别置信度：{d['confidence']:.2f}\n库位：{d['warehouse_position']}\nYOLO26：{'已加载' if d['yolo26_used'] else '场景检测模式'}\n超图关联数：{d['hyperedge_count']}")
        self.stack.setCurrentIndex(1)

    def open_image(self):
        path,_=QFileDialog.getOpenFileName(self,"选择钢卷图像","","Images (*.jpg *.jpeg *.png *.bmp)")
        if not path:return
        frame=cv2.imread(path); det,draw=self.pipeline.process_frame(frame); self.show_frame(draw,det)

    def open_video(self):
        path,_=QFileDialog.getOpenFileName(self,"选择钢卷视频","","Videos (*.mp4 *.avi *.mov *.mkv)")
        if not path:return
        if self.video:self.video.release()
        self.video=cv2.VideoCapture(path)
        if not self.video.isOpened(): QMessageBox.warning(self,"提示","视频无法打开"); return
        self.timer.start(80)
        self.stack.setCurrentIndex(1)

    def next_video_frame(self):
        if not self.video:return
        ok,frame=self.video.read()
        if not ok:
            self.timer.stop(); self.video.release(); self.video=None; return
        det,draw=self.pipeline.process_frame(frame); self.show_frame(draw,det)

    def create_task(self):
        if not self.current_detections:
            QMessageBox.information(self,"提示","请先进行钢卷AI识别"); return
        tasks=self.pipeline.create_tasks(self.current_detections); self.populate_tasks(tasks); self.stack.setCurrentIndex(2)

    def schedule(self):
        if not self.current_detections:
            QMessageBox.information(self,"提示","请先进行钢卷AI识别"); return
        tasks=self.pipeline.create_tasks(self.current_detections); self.populate_tasks(tasks); self.stack.setCurrentIndex(2)

    def populate_tasks(self,tasks):
        self.table.setRowCount(0)
        for t in tasks:
            r=self.table.rowCount(); self.table.insertRow(r)
            for c,val in enumerate([t["task_id"],t["coil_id"],t["crane"],t["target"],t["status"]]): self.table.setItem(r,c,QTableWidgetItem(str(val)))

    def clear_all(self):
        self.current_detections=[]; self.image_label.clear(); self.image_label.setText("等待输入图像或视频"); self.info.setText("识别结果将在此显示"); self.stack.setCurrentIndex(0)
