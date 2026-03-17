<div align="center">
  <a href="./README_en.md">English</a> | 简体中文
</div>

# LoveJournal v1 (经典 Flask 生活记录系统)

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 是本生活记录系统的初始技术演进版本。项目基于经典的 **Flask** 框架与服务器端渲染 (SSR) 方案构建，旨在提供一个稳健、温馨的私密回忆归档平台。作为后续高性能异步版本 (Lovejournal-New) 的架构起源，本项目完整保留了初期在数据持久化、媒体资产管理与响应式布局方面的工程实践。

## 🏛️ 核心设计与功能实践

### 1. 线性时间轴建模 (Sequential Modeling)
利用 **Flask-SQLAlchemy** 实现对记录条目的高效编排。
- **逻辑分层**: 采用模型（Models）与 视图（Views）分离的设计模式，确保了业务逻辑的清晰度。
- **时间序检索**: 通过后端查询优化，实现基于时间戳的深度排序，为用户提供符合直觉的历史记忆回溯路径。

### 2. 传统 SSR 与响应式视图
- **Jinja2 模板工程**: 利用模板继承与组件化思想，减少了 HTML 冗余，实现了视图层的高可复用性。
- **Bootstrap 5 栅格系统**: 严格遵循移动优先（Mobile First）原则，确保页面在各类移动设备与桌面端浏览器下均具备一致的视觉感官。

### 3. 基础媒体资产治理
- **上传管道**: 实现了包含文件名安全脱敏、类型校验与自动重命名的文件上传管道。
- **物理存储**: 基于本地文件系统进行分级存储，为后续的对象存储迁移预留了逻辑接口。

## 📂 项目工程结构

```text
lovejournal/
├── ljapp/              # 核心应用逻辑目录
│   ├── models.py       # 数据库实体定义 (SQLAlchemy)
│   └── views.py        # 路由处理器与业务控制器
├── static/             # 静态资产：包含全局 CSS、Vanilla JS 与 UI 图像
├── templates/          # 基于 Jinja2 的 HTML 组件模板池
├── migrations/         # 结构化的数据库版本迁移历史
├── instance/           # 包含本地测试环境的 SQLite 数据文件
├── app.py              # Flask 应用引导程序、插件初始化与全局入口
└── README.md           # 技术规格说明与开发规范
```

## 🚀 后后续版本建议
本项目作为 **v1 初始版** 已进入维护状态。如需追求更现代的交互体验与极致性能，请参阅后续版本：
👉 **[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)** (FastAPI + React 19 + 高德地图)

## 许可证
本项目采用 MIT License 协议。
