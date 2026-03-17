# LoveJournal v1 (爱意笔记 - 经典技术栈版)

[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?logo=sqlalchemy)](https://www.sqlalchemy.org/)

LoveJournal v1 是本项目的初始技术迭代版本。系统基于轻量级的 Flask 框架与传统的服务器端渲染 (SSR) 技术构建，旨在提供一个温馨且实用的私密回忆归档平台。本项目作为后续高性能 FastAPI 版本 (Lovejournal-New) 的演进基石，完整保留了初期架构的设计思考。

## 核心设计

- 回忆持久化归档: 实现文字记录与多图组合的结构化存储，支持基于时间维度的线性归档。
- 线性时间轴交互: 利用 SQLAlchemy 进行后端数据编排，为用户提供清晰的历史记忆回溯路径。
- 自动化媒体资产治理: 内置安全的文件上传重命名与防重存储机制，确保静态资产的鲁棒性。
- 响应式视图工程: 结合 Bootstrap 5 样式标准，实现对移动端与桌面端的兼容性覆盖。
- 稳健的安全拦截: 在业务层实现了完善的请求校验、异常捕获与基础的前后端交互加固。

## 技术栈

- Web 核心框架: Flask
- 持久层协议: Flask-SQLAlchemy
- 模板渲染引擎: Jinja2
- 视觉框架: Bootstrap 5
- 后端语言标准: Python 3.x
- 文件安全工具: Werkzeug

## 项目结构

```text
.
├── ljapp               # 核心业务逻辑实现
├── static              # 静态视觉资产 (CSS, JS, Images)
├── templates           # 基于 Jinja2 的 HTML 视图模板
├── migrations          # 结构化的数据库迁移记录
├── app.py              # 服务入口定义
└── README.md
```

## 快速启动

### 1. 基础依赖部署
```bash
pip install flask flask_sqlalchemy requests werkzeug
```

### 2. 数据库与环境初始化
系统默认为 SQLite 物理存储，可在 `app.py` 中自定义配置。

### 3. 服务端启动
```bash
python app.py
```

## 版本演进说明
本仓库为 v1 经典版。如需体验更高并发性能、基于 React 19 的交互设计以及深度地图空间集成功能，请关注本项目的后续版本：[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)。

## 许可证
本项目采用 MIT License 协议。

---
Developed by [saudademjj](https://github.com/saudademjj)
