# LoveJournal（Flask 版）

一个基于 Flask 的恋爱日记 Web 应用，支持日记、照片、纪念日、地图定位与时间轴展示。

## 功能概览

- 日记管理：支持 Markdown 内容与标签提取
- 照片管理：支持上传、编辑、删除与图片展示
- 纪念日管理：支持日期记录、倒计时/已过天数展示
- 时间轴：按时间统一聚合三类内容，支持检索与分页加载
- 地图视图：根据地点文本或经纬度展示地图标记
- 登录认证：基于 `Flask-Login` 的登录态管理

## 技术栈

- 后端：Flask、Flask-SQLAlchemy、Flask-Migrate、Flask-Login
- 数据库：SQLite（默认）/ PostgreSQL（通过 `DATABASE_URL` 切换）
- 前端：Jinja2 模板 + 原生 HTML/CSS/JavaScript
- 地图：高德地理编码接口

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
└── README.md
```

## 环境要求

- Python 3.8+
- pip

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/saudademjj/lovejournal.git
cd lovejournal
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install flask flask-sqlalchemy flask-migrate flask-login bleach markdown requests
```

### 3. 初始化数据库

```bash
flask --app app.py db upgrade
```

### 4. 创建登录用户

```bash
flask --app app.py create-user
```

### 5. 启动应用

```bash
flask --app app.py run
# 或 python app.py
```

默认访问：`http://127.0.0.1:5000`

## 环境变量

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `FLASK_SECRET_KEY` | Flask 会话密钥 | `your-secret-key` |
| `DATABASE_URL` | 数据库连接串 | `sqlite:///instance/lovejournal.sqlite` |
| `AMAP_WEB_KEY` | 高德地理编码 Key | 代码内默认值 |

## 常用 CLI 命令

```bash
# 创建或更新用户
flask --app app.py create-user

# 从旧 SQLite 数据导入当前数据库
flask --app app.py import-sqlite /path/to/old.sqlite
```

## 主要接口（需要登录）

- 页面路由：
  - `/` 时间轴主页
  - `/anniversaries` 纪念日页
  - `/map` 地图页
- API 路由：
  - `GET /api/timeline` 返回时间轴分页 HTML 片段

## 常见问题

1. 上传图片失败
- 检查文件格式是否在允许列表（png/jpg/jpeg/gif/webp），并确认文件大小不超过 16MB。

2. 地图无法定位
- 检查 `AMAP_WEB_KEY` 是否有效，网络是否可访问高德地理编码接口。

3. 无法登录
- 确认已执行 `create-user` 创建账号。

## 生产建议

- 将 `FLASK_SECRET_KEY` 改为高强度随机值
- 使用 PostgreSQL 并启用备份
- 通过反向代理（Nginx/Caddy）提供 HTTPS
- 把 `instance/` 目录加入备份策略（包含数据库与上传文件）

## 许可证

当前仓库未显式提供 License 文件。
