# 💕 LoveJournal

一个基于 Flask 的恋爱日记 Web 应用，支持日记撰写、照片上传、纪念日管理、地图定位和时间轴展示。

## ✨ 功能特性

- 📝 **日记管理** — 支持 Markdown 编辑和标签分类
- 📷 **照片上传** — 支持 PNG/JPG/JPEG/GIF/WebP 格式，最大 16MB
- 🎉 **纪念日管理** — 记录和追踪重要日期，自动计算距今天数
- 🗺️ **地图定位** — 集成高德地图 API，支持地理位置记录与地图展示
- 🔒 **用户认证** — 基于 Flask-Login 的登录系统
- 📅 **时间轴** — 按时间线展示所有记录，支持无限滚动

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python / Flask / Flask-SQLAlchemy / Flask-Migrate / Flask-Login |
| 数据库 | SQLite（默认）/ 支持通过环境变量切换 |
| 前端 | HTML / CSS / JavaScript（Jinja2 模板渲染） |
| 地图 | 高德地图 Web API |

## 📁 项目结构

```
lovejournal/
├── app.py                  # 应用入口
├── ljapp/
│   ├── __init__.py         # Flask App 工厂与配置
│   ├── models.py           # 数据模型（User, Entry, KeyDate, Photo）
│   ├── utils.py            # 工具函数（Markdown 渲染、地理编码、标签提取）
│   └── routes/
│       ├── main.py         # 主页路由
│       ├── auth.py         # 认证路由
│       └── api.py          # API 路由
├── templates/              # Jinja2 模板
│   ├── base.html           # 基础模板
│   ├── index.html          # 主页 / 时间轴
│   ├── login.html          # 登录页
│   ├── map.html            # 地图页
│   └── anniversaries.html  # 纪念日页
├── static/                 # 静态资源
│   └── geo/                # 地理数据
├── migrations/             # 数据库迁移文件
└── instance/               # 实例数据（SQLite 数据库、上传文件）
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装与运行

```bash
# 克隆仓库
git clone https://github.com/saudademjj/lovejournal.git
cd lovejournal

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install flask flask-sqlalchemy flask-migrate flask-login bleach markdown requests werkzeug

# 初始化数据库
flask db upgrade

# 创建用户
flask create-user

# 启动应用
flask run
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `FLASK_SECRET_KEY` | Flask 密钥 | `your-secret-key` |
| `DATABASE_URL` | 数据库连接串 | SQLite（instance 目录下） |
| `AMAP_WEB_KEY` | 高德地图 Web API Key | 内置默认值 |

### CLI 命令

```bash
flask create-user           # 创建或更新登录用户
flask import-sqlite <path>  # 从旧版 SQLite 导入数据
```

## 📄 License

MIT
