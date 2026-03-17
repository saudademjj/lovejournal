<div align="center">
  <a href="./README.md">简体中文</a> | <a href="./README_en.md">English</a>
</div>

# LoveJournal v1 (初始 Flask 开发版本 / Initial Flask Development Version)

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 是本记录系统的初始技术演进版本。项目基于经典的 Flask 框架与服务器端渲染 (SSR) 方案，旨在提供一个稳健的个人/伴侣回忆归档平台。本项目完整保留了开发初期的架构思考，是后续高性能异步版本 (Lovejournal-New) 的技术基石。

LoveJournal v1 is the initial technical evolution of the record system. Built with the classic Flask framework and SSR approach, it provides a robust memory archiving platform for individuals/couples. Preserving the original architectural concepts, this project serves as the technical foundation for the subsequent high-performance async version (Lovejournal-New).

## 核心技术实践 / Core Technical Practices

- **线性数据建模**: 基于 Flask-SQLAlchemy 实现的顺序时间轴存储，保障了记录的因果逻辑一致性。 / Sequential timeline storage via Flask-SQLAlchemy.
- **响应式渲染工程**: 利用 Jinja2 模板引擎结合 Bootstrap 5 栅格系统，实现多端适配的 UI 表现。 / Multi-device UI via Jinja2 and Bootstrap 5.
- **基础资产治理**: 实现了结构化的本地文件上传校验与存储分级。 / Structured local file upload validation and tiered storage.

## 项目结构图 / Project Structure

```text
lovejournal/
├── ljapp/              # 应用核心目录，包含视图逻辑与蓝图配置 / Core App logic
├── static/             # 包含 CSS、JS 与 视觉资产的静态资源目录 / Assets
├── templates/          # 基于 Jinja2 的 HTML 视图组件模板 / View templates
├── migrations/         # 数据库版本迁移的历史记录 / DB migrations
├── app.py              # Flask 应用引导程序与环境初始化入口 / Entry point
└── README.md           # 技术规范文档 / Technical documentation
```

## 快速运行指南 / Quick Start

### 1. 依赖安装 / Dependencies
```bash
pip install flask flask_sqlalchemy requests werkzeug
```

### 2. 环境引导 / Launch
```bash
# 默认采用本地 SQLite 存储
python app.py
```

## 后后续版本建议 / Successor
如需追求基于 React 19 的交互体验、FastAPI 的异步性能以及高德地图深度集成，请参考： / For React 19, FastAPI, and AMap integration, see: **[Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)**

## 许可证 / License
本项目遵循 MIT License 协议。 / Licensed under the MIT License.
