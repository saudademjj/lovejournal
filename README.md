<div align="center">
  <a href="./README_en.md">English</a> | 简体中文
</div>

# LoveJournal v1 -- 经典 Flask 生活记录系统

![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat-square&logo=flask)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square&logo=sqlalchemy)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap)

LoveJournal v1 是本生活记录系统的初始技术演进版本。项目基于经典的 Flask 框架与服务器端渲染（SSR）方案构建，旨在提供一个稳健、温馨的私密回忆归档平台。作为后续高性能异步版本 [Lovejournal-New](https://github.com/saudademjj/Lovejournal-New) 的架构起源，本项目完整保留了初期在数据持久化、媒体资产管理与响应式布局方面的工程实践。

## 核心功能

### 多维记忆管理
- 支持图文并茂的 Markdown 日记创建与编辑
- 无损图片画廊上传与浏览
- 精确到天的纪念日追踪与倒计时提醒
- 多类型数据的统一管理界面

### 全局时间轴视界
- 将所有类型的数据流（日记、照片、纪念日）按时间线统一聚合
- 支持分页浏览与全文检索
- 基于时间戳的深度排序，提供符合直觉的历史回溯路径

### 地理位置足迹
- 集成高德地图（AMap）地理编码服务
- 直观展示每一次记录的空间坐标
- 地图标记与记忆条目的关联浏览

### 安全与私密
- 基于 Flask-Login 的会话管理机制
- 用户认证与访问控制
- 确保私人回忆不被未授权访问

## 技术架构

### 后端

- Flask 3.0：经典的 Python Web 微框架
- Flask-SQLAlchemy：ORM 数据模型与查询构建
- Flask-Login：用户会话管理与认证
- Flask-Migrate / Alembic：数据库迁移版本控制

### 前端（SSR）

- Jinja2 模板引擎：模板继承与组件化设计，减少 HTML 冗余，提高视图层复用性
- Bootstrap 5.3：移动优先的响应式栅格系统，确保各类设备下的一致视觉体验
- 原生 JavaScript：DOM 交互与动态效果

### 数据与存储

- SQLAlchemy ORM：模型与视图分离的设计模式，业务逻辑清晰
- 文件上传管道：包含文件名安全脱敏、类型校验与自动重命名
- 本地文件系统分级存储：为后续对象存储迁移预留逻辑接口

### 地理服务

- 高德地图地理编码 API：地址文本到坐标的转换
- 地图标记渲染：基于坐标数据的可视化展示

## 目录结构

```text
lovejournal/
├── app.py                  # Flask 应用入口
├── ljapp/                  # 应用主包
│   ├── __init__.py         # 应用工厂与扩展初始化
│   ├── models/             # SQLAlchemy 模型定义
│   │   └── ...             # 日记、照片、纪念日等数据模型
│   ├── views/              # 路由处理器 / 蓝图
│   │   └── ...             # 认证、日记、画廊、时间线等视图
│   ├── templates/          # Jinja2 模板（含模板继承）
│   │   ├── base.html       # 基础布局模板
│   │   └── ...             # 各功能页面模板
│   └── static/             # CSS、JS、上传的媒体文件
├── migrations/             # Alembic / Flask-Migrate 数据库迁移
├── instance/               # 实例级配置（不纳入版本控制）
└── README.md
```

## 快速开始

### 环境要求

- Python >= 3.10
- SQLite（默认）或 PostgreSQL

### 1. 克隆与环境准备

```bash
git clone https://github.com/saudademjj/lovejournal.git
cd lovejournal
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 环境配置

创建 `.env` 或在 `instance/` 目录下配置：

```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/app.db  # 或 PostgreSQL 连接串
AMAP_API_KEY=your-amap-key              # 高德地图 API 密钥
```

### 3. 数据库初始化

```bash
flask db upgrade
```

### 4. 启动应用

```bash
flask run
```

访问 `http://localhost:5000` 即可使用。

## 与 LoveJournal-New 的关系

本项目是生活记录系统的 v1 版本，后续已演进为基于 FastAPI + React 的高性能异步架构：

| 维度 | v1（本项目） | v2（Lovejournal-New） |
|------|-------------|----------------------|
| 后端 | Flask（同步） | FastAPI（异步） |
| 前端 | Jinja2 SSR + Bootstrap | React SPA + Tailwind CSS |
| 数据库 | Flask-SQLAlchemy | SQLAlchemy 2.0 Async + asyncpg |
| 地图 | 基础地理编码 | 深度交互 + 点聚合 + GIST 索引 |
| 渲染模式 | 服务端渲染 | 客户端渲染 + API 分离 |

v1 版本作为架构起源完整保留，适合学习 Flask 全栈开发模式与 SSR 工程实践。

## 许可证

MIT License
