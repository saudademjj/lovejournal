# LoveJournal v1 (初始 Flask 开发版本 / Initial Flask Development Version)

LoveJournal 的初始原型版本，基于 Flask 构建，完整保留了初期架构设计思路。

The initial prototype of LoveJournal, built with Flask, preserving the original architectural design concepts.

## 核心特性 / Core Features

- 线性时间轴 (Linear Timeline):
    - 基于 Flask-SQLAlchemy 实现的顺序记录检索。 / Sequential record retrieval via Flask-SQLAlchemy.

- 基础资产治理 (Basic Asset Management):
    - 实现本地文件上传与静态资源服务。 / Local file upload and static asset serving.

## 技术栈 / Technical Stack

- Backend: Flask, Python 3.x.
- Database: SQLite / PostgreSQL (via SQLAlchemy).
- UI: Bootstrap 5, Jinja2.

## 项目结构 / Project Structure

```text
lovejournal/
├── ljapp/              # 核心 Flask 应用逻辑 / Core Flask app
├── static/             # 样式与前端脚本 / Assets
├── templates/          # Jinja2 视图模板 / View templates
└── app.py              # 入口启动程序 / Entry point
```

## 后续演进 / Successor
请参考高性能异步版本 / For the successor version see: [Lovejournal-New](https://github.com/saudademjj/Lovejournal-New)

## 许可证 / License
本项目采用 [MIT License](LICENSE) 协议。 / This project is licensed under the MIT License.
