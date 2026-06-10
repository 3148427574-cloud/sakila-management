# Sakila DVD 租赁管理系统

基于 MySQL Sakila 示例数据库的 DVD 租赁管理系统，使用 Python tkinter 构建 GUI 界面。

## 技术栈

- Python 3.12 + tkinter
- MySQL 8.0 + Sakila Sample Database
- pymysql

## 项目结构

```
sakila-management/
├── db.py            # 数据库连接封装
├── main.py          # 登录入口 + 主界面路由
├── film_ui.py       # 电影管理
├── actor_ui.py      # 演员管理
├── customer_ui.py   # 客户管理
├── rental_ui.py     # 租赁处理
├── inventory_ui.py  # 库存管理
└── report/          # 开发文档
```

## 快速开始

### 1. 安装 Sakila 数据库

```bash
curl -sL https://downloads.mysql.com/docs/sakila-db.tar.gz -o sakila-db.tar.gz
tar -xzf sakila-db.tar.gz
mysql -u root -p < sakila-db/sakila-schema.sql
mysql -u root -p < sakila-db/sakila-data.sql
```

### 2. 安装依赖

```bash
pip install pymysql
```

### 3. 修改数据库配置

编辑 `db.py`，修改 `DB_CONFIG` 中的 `host`、`user`、`password`。

### 4. 运行

```bash
python main.py
```

### 5. 登录

使用 Sakila 内置 staff 账号：
| 用户名 | 门店 |
|--------|------|
| Mike   | 1    |
| Jon    | 2    |

## 功能模块

| 模块 | 功能 | 涉及表 |
|------|------|--------|
| 租赁处理 | 影片租赁、归还、付款 | rental, inventory, payment, customer |
| 客户管理 | 客户信息 CRUD | customer, address, city, country |
| 库存管理 | 各门店影片拷贝管理 | inventory, film, store |
| 电影管理 | 电影信息及分类管理 | film, film_category, category, film_actor |
| 演员管理 | 演员信息及参演作品 | actor, film_actor |
