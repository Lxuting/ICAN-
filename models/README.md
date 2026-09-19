# 模型权重

项目默认使用 Ultralytics 官方 YOLO26n 预训练权重 `yolo26n.pt` 作为基础视觉模型。

GitHub 仓库不强制提交二进制权重；运行时如果 `models/yolo26n.pt` 不存在，程序会尝试通过 Ultralytics 获取官方权重（需要网络）。

如果已提前下载，请将文件放在：

`models/yolo26n.pt`
