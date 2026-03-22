# 爬墙日历 (Climbing Calendar)

一个支持多用户独立数据的爬墙记录Web应用。

## 功能特性

- ✅ 记录每次爬墙（日期、岩馆、线路、成绩、搭子）
- ✅ 自定义岩馆和搭子配置
- ✅ 多用户支持，每人独立账号和数据
- ✅ 数据导出/导入（JSON格式）
- ✅ 成绩统计、趋势分析、最佳搭子评选
- ✅ 用户登录/注册功能
- ✅ 获奖台展示（前三名搭子）

## 技术架构

- **前端**：HTML + CSS + JavaScript（原生）
- **后端**：Python Flask
- **数据库**：SQLite
- **部署**：阿里云轻量服务器（Ubuntu）

## 目录结构

```
climbing-calendar/
├── app.py              # Flask 后端主程序
├── database.py         # 数据库初始化
├── models.py          # 数据模型
├── static/
│   ├── calendar.html   # 主页面
│   └── login.html     # 登录页面
├── data/
│   └── climbing.db    # SQLite 数据库
└── README.md          # 本文件
```

## 快速开始

### 1. 本地运行

```bash
# 克隆项目
git clone https://github.com/royadam21/climbing-calendar.git
cd climbing-calendar

# 安装依赖
pip3 install flask

# 启动服务
python3 app.py
```

访问 http://localhost:5000

### 2. 服务器部署

```bash
# 服务器上安装 Flask
apt update
apt install -y python3 python3-pip
pip3 install flask --break-system-packages

# 克隆项目
cd /var/www
git clone https://github.com/royadam21/climbing-calendar.git
cd climbing-calendar

# 启动服务（后台运行）
nohup python3 app.py > server.log 2>&1 &

# 开放端口
ufw allow 5000/tcp
```

访问 http://服务器IP:5000

### 3. 阿里云安全组配置

需要在阿里云控制台添加安全组规则：
- 协议：TCP
- 端口：5000
- 来源：0.0.0.0/0

## API 接口

### 用户认证
- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录
- `POST /api/logout` - 用户登出
- `GET /api/check_login` - 检查登录状态

### 爬墙记录
- `GET /api/records` - 获取当前用户所有记录
- `POST /api/records` - 添加新记录
- `PUT /api/records/<id>` - 更新记录
- `DELETE /api/records/<id>` - 删除记录
- `POST /api/records/clear` - 清空所有记录

### 配置管理
- `GET /api/gyms` - 获取岩馆列表
- `POST /api/gyms` - 添加岩馆
- `DELETE /api/gyms/<id>` - 删除岩馆
- `POST /api/gyms/clear` - 清空岩馆
- `GET /api/partners` - 获取搭子列表
- `POST /api/partners` - 添加搭子
- `DELETE /api/partners/<id>` - 删除搭子
- `POST /api/partners/clear` - 清空搭子

### 数据同步
- `GET /api/export` - 导出数据（JSON格式）
- `POST /api/import` - 导入数据（从JSON）

### 其他
- `POST /api/feedback` - 意见反馈（发送邮件）

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

## 更新日志

### 2026-03-22
- **记录块结构大改版**：三部分结构（标题+按钮行、2x2信息网格、备注分隔线）
- **取消按钮样式修复**：去除粉色渐变覆盖、加box-shadow:none、等宽flex:1、圆角一致
- **返回图标替换**：设置/统计页面使用自定义PNG返回图标
- **Top5统计bug修复**：修复变量重复声明导致统计失效问题
- **全局岩馆/搭子共享**：gyms表迁移为全局共享（去掉user_id列）
- **管理员权限控制**：岩馆配置模块仅管理员可见
- **新增按名称删除API**：支持通过名称删除岩馆/搭子
- **max_grade保存功能**：在user_settings表保存用户最高级别
- **设置页面UI优化**：删除后前端立即更新（pendingOps Set防重复）、实时保存、自定义Toast提示框
- **修复路由重复定义**：save_max_grade、get_max_grade、import_data_api

### 2026-03-19
- 移动端UI优化
- 日历格子宽高比调整为3:4
- 日历当天日期红色边框高亮
- 日历日期限制：未来日期不可选，月份不能切换到未来
- 统计面板日期查询改为弹窗选择
- 设置弹窗改为底部悬浮取消/保存按钮
- 岩馆品牌分类改为可展开/收起
- 岩馆和搭子添加改为弹窗选择
- 清空数据和退出登录二次确认改弹窗
- 数据库时区迁移为北京时间（+8小时）

### 2026-03-18
- 全新Flask+SQLite版本
- 支持用户登录/注册
- 多用户数据隔离
- 全新UI设计，深色主题
- 统计面板优化
- 最佳搭子颁奖台展示

---
让你的每一次努力都留下印记！🧗‍♀️
