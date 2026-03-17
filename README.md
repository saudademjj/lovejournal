# LoveJournal

[English](README_en.md) | 简体中文

`LoveJournal` 是一个基于 Flask 的恋爱日记 Web 应用，围绕“记录、回看、纪念、展示”这几个使用场景，提供日记、照片、纪念日、地图和时间轴等功能。相比重构版 `LoveJournal New`，这里保留的是更传统的一体化 Web 架构。

## 核心功能

- 日记管理，支持 Markdown 内容和标签提取
- 照片上传、编辑、删除与展示
- 纪念日管理，支持倒计时与已过天数
- 时间轴聚合视图，统一浏览多类型内容
- 地图页，根据地点或经纬度展示标记
- 基于 `Flask-Login` 的登录认证

## 技术栈

- 后端：`Flask`、`Flask-SQLAlchemy`、`Flask-Migrate`、`Flask-Login`
- 数据库：默认 `SQLite`，可切换到 `PostgreSQL`
- 前端：`Jinja2` 模板 + 原生 HTML/CSS/JavaScript
- 地图能力：高德地理编码接口

## 仓库结构

```text
lovejournal/
├── app.py
├── ljapp/
│   ├── __init__.py
│   ├── models.py
│   ├── utils.py
│   └── routes/
│       ├── auth.py
│       ├── main.py
│       └── api.py
├── templates/
├── static/
├── migrations/
├── instance/
├── README.md
└── README.en.md
```

## 环境要求

- Python 3.8+
- pip

## 快速开始

```bash
git clone https://github.com/saudademjj/lovejournal.git
cd lovejournal
python -m venv .venv
source .venv/bin/activate
pip install flask flask-sqlalchemy flask-migrate flask-login bleach markdown requests
flask --app app.py db upgrade
flask --app app.py create-user
flask --app app.py run
```

默认访问地址：`http://127.0.0.1:5000`

## 环境变量

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | Flask 会话密钥 | `your-secret-key` |
| `DATABASE_URL` | 数据库连接串 | `sqlite:///instance/lovejournal.sqlite` |
| `AMAP_WEB_KEY` | 高德地理编码 Key | 代码内默认值 |

## 常用 CLI

```bash
flask --app app.py create-user
flask --app app.py import-sqlite /path/to/old.sqlite
```

## 页面与接口

- 页面：
  - `/`
  - `/anniversaries`
  - `/map`
- API：
  - `GET /api/timeline`

## 生产建议

- 将 `FLASK_SECRET_KEY` 改为高强度随机值
- 使用 PostgreSQL 并做好备份
- 通过 Nginx 或 Caddy 提供 HTTPS
- 将 `instance/` 目录纳入备份策略

## 许可证

本仓库采用 MIT License，详见 [LICENSE](./LICENSE)。
