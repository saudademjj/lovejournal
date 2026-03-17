<div align="center">
  <a href="./README_en.md">English</a> | 简体中文
</div>

# LoveJournal v1 (经典 Flask 生活记录系统)

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 是本记录系统的初始技术演进版本。项目基于经典的 **Flask** 框架与服务器端渲染 (SSR) 方案构建，旨在提供一个稳健、温馨的个人/伴侣回忆归档平台。作为后续高性能异步版本 (Lovejournal-New) 的架构起源，本项目完整保留了开发初期的设计思考与工程实践。

## 核心设计与功能实践

### 1. 线性时间轴建模
利用 **Flask-SQLAlchemy** 实现对记录条目的顺序编排。系统通过后端逻辑对时间戳进行深度排序，为用户提供符合直觉的历史记忆回溯路径。

### 2. 响应式视图渲染
- **Jinja2 模板**: 采用解耦的模板继承机制，确保视图层的高度可复用性。
- **Bootstrap 5 样式标准**: 结合栅格系统实现对移动端与桌面端的无缝适配，提供一致的视觉感官体验。

### 3. 基础媒体资产治理
实现了结构化的本地文件上传校验、重命名与持久化存储机制，确保了静态资源在物理存储层面的安全性与唯一性。

## 技术栈简析

- **后端核心**: Flask (Python 3.x)。
- **持久层**: Flask-SQLAlchemy (支持 SQLite/PostgreSQL)。
- **样式框架**: Bootstrap 5。
- **文件安全**: Werkzeug (用于安全的文件名解析与上传处理)。

## 项目工程结构

```text
lovejournal/
├── ljapp/              # 核心应用逻辑目录 (包含视图函数与蓝图配置)
├── static/             # 静态资源存放目录 (CSS, JavaScript, Images)
├── templates/          # 基于 Jinja2 的 HTML 视图组件模板
├── migrations/         # 数据库版本迁移的历史记录
├── instance/           # 包含 SQLite 数据库文件的实例目录
├── app.py              # Flask 应用引导程序与环境初始化入口
└── README.md           # 中文技术规范说明文档
```

## 后续演进建议
本项目作为 **v1 初始版** 已进入维护阶段。如需体验基于 React 19 的交互动效、FastAPI 的异步并发性能以及高德地图的深度空间集成，请关注：**[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)**。

## 许可证
本项目遵循 MIT License 协议。
