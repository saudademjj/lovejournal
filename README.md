# LoveJournal v1 (生活记录 - 初始版)

[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?logo=sqlalchemy)](https://www.sqlalchemy.org/)

LoveJournal v1 是本项目的初始技术版本。系统基于轻量级的 Flask 框架构建，提供了私密的回忆归档功能。本项目作为后续 FastAPI 版本 (Lovejournal-New) 的演进基础。

## 核心功能

- 回忆归档: 文字记录与图片组合的存储展示。
- 时间轴展示: 利用 SQLAlchemy 后端查询，按时间顺序呈现历史记录。
- 资产管理: 实现了基础的图片上传与本地化存储机制。
- 响应式视图: 基于 Bootstrap 5 构建，适配移动端与桌面端。

## 技术栈

- 框架: Flask
- ORM: Flask-SQLAlchemy
- 渲染: Jinja2, Bootstrap 5
- 语言: Python 3.x

## 项目结构

```text
.
├── ljapp               # 业务逻辑
├── static              # 静态资源 (CSS, JS)
├── templates           # HTML 模板
├── migrations          # 数据库迁移
├── app.py              # 入口
└── README.md
```

## 快速启动

### 1. 依赖
`pip install flask flask_sqlalchemy requests werkzeug`

### 2. 运行
`python app.py`

## 版本说明
本项目为 **v1 初始版**。后续高性能版本请关注：[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)。

## 许可证
MIT License
