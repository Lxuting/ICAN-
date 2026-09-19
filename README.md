# 钢智灵枢

**面向钢铁仓储的多模态AI感知与智能决策软件平台**

## 1. 项目简介

钢智灵枢面向钢铁仓储中的钢卷识别、仓储状态分析、任务创建、天车调度、异常监测与状态反馈等业务环节，构建“感知—分析—决策—执行—反馈”的软件闭环。

核心技术模块包括：

- YOLO26n 基础视觉模型接口
- 李代数物理状态表达
- 超图高阶关联建模
- 粒球特征聚合
- QR 二维码识别
- 钢卷场景视觉候选检测
- 仓储数字孪生状态管理
- PPO-compatible 智能调度接口
- PyQt5 软件交互界面

## 2. 软件运行

```bash
pip install -r requirements.txt
python main.py
```

Windows 也可以双击：

```text
run.bat
```

## 3. YOLO26n 权重

默认路径：

```text
models/yolo26n.pt
```

如果本地没有权重，可以运行：

```bash
python download_weight.py
```

需要说明：官方 YOLO26n 是通用预训练权重，并非钢卷专用训练权重。本项目将其作为基础视觉模型，并结合钢卷场景视觉解析、二维码识别以及物理先验模块完成软件演示。

## 4. 代码结构

```text
钢智灵枢/
├── main.py
├── download_weight.py
├── requirements.txt
├── run.bat
├── README.md
├── app/
│   ├── core/pipeline.py
│   ├── perception/
│   │   ├── model_loader.py
│   │   ├── steel_detector.py
│   │   ├── lie_feature.py
│   │   ├── hypergraph.py
│   │   └── granular_ball.py
│   ├── localization/pose.py
│   ├── digital_twin/state.py
│   ├── scheduling/
│   │   ├── ppo_agent.py
│   │   └── scheduler.py
│   └── ui/
│       ├── login_window.py
│       ├── main_window.py
│       └── theme.py
├── models/README.md
└── docs/
```

## 5. 软件操作流程

登录系统 → 查看仓储状态 → 钢卷AI识别 → 信息确认 → 创建任务 → 智能调度 → 查看执行状态 → 异常处理 → 任务完成与状态更新。

## 6. 提交说明

GitHub 建议提交完整源代码、README、requirements.txt 和运行说明。演示视频与应用计划按比赛系统要求单独提交。
