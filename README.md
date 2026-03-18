# 爬墙日历 (Climbing Calendar)--给攀岩人的一份礼物

一个支持多用户独立数据的爬墙记录Web应用。



## 功能特性

- ✅ 记录每次爬墙（日期、岩馆、线路、成绩、搭子）
- ✅ 自定义岩馆和搭子配置
- ✅ 多用户支持，每人独立账号和数据
- ✅ 数据导出/导入（JSON格式）
- ✅ 成绩统计、趋势分析、最佳搭子评选

## 让你的每一次努力都留下印记！


## 技术架构

- **前端**：HTML + CSS + JavaScript（原生）
- **后端**：Python Flask
- **数据库**：SQLite
- **部署**：阿里云轻量服务器（Ubuntu）

## 数据库结构

### 用户表 (users)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | TEXT | 用户名（唯一） |
| password | TEXT | 密码（加密存储） |
| created_at | DATETIME | 创建时间 |

### 爬墙记录表 (records)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，关联用户 |
| date | DATE | 爬墙日期 |
| gym | TEXT | 岩馆名称 |
| grade | TEXT | 难度等级 |
| result | TEXT | 成绩（红点/首攀等） |
| partner | TEXT | 搭子 |
| note | TEXT | 备注 |
| created_at | DATETIME | 创建时间 |

### 岩馆配置表 (gyms)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，关联用户 |
| gym_name | TEXT | 岩馆名称 |
| wall_type | TEXT | 墙型（抱石/先锋等） |

### 搭子配置表 (partners)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 外键，关联用户 |
| name | TEXT | 搭子名称 |

## API 接口

### 用户认证
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出

### 爬墙记录
- `GET /api/records` - 获取当前用户所有记录
- `POST /api/records` - 添加新记录
- `PUT /api/records/<id>` - 更新记录
- `DELETE /api/records/<id>` - 删除记录

### 配置管理
- `GET /api/gyms` - 获取岩馆列表
- `POST /api/gyms` - 添加岩馆
- `GET /api/partners` - 获取搭子列表
- `POST /api/partners` - 添加搭子

### 数据同步
- `POST /api/import` - 导入数据（从JSON）
- `GET /api/export` - 导出数据（JSON格式）

## 部署指南

### 1. 服务器环境
```bash
# 安装 Python 和 Flask
apt update
apt install -y python3 python3-pip
pip3 install flask

# 克隆项目
git clone https://github.com/royadam21/climbing-calendar.git
cd climbing-calendar
```

### 2. 配置启动
```bash
# 首次运行会自动创建数据库
python3 app.py
```

### 3. 访问应用
```
http://服务器IP:5000
```

### 4. Nginx 反向代理（可选）
配置 Nginx 将 80 端口转发到 5000。

## 目录结构

```
climbing-calendar/
├── app.py              # Flask 后端主程序
├── database.py         # 数据库初始化
├── models.py           # 数据模型
├── static/
│   └── index.html      # 前端页面（改造后）
├── templates/
│   └── login.html      # 登录页面
├── static/
│   ├── css/
│   │   └── style.css   # 样式
│   └── js/
│       └── app.js      # 前端脚本
├── data/
│   └── climbing.db     # SQLite 数据库
└── README.md           # 本文件
```
