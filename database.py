# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建 SQLite 数据库和表结构
"""

import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'climbing.db')

def init_database():
    """初始化数据库，创建所有表"""
    
    # 确保 data 目录存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 设置时区为东8区（北京时区）
    cursor.execute("PRAGMA timezone = '+08:00'")
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 为已有数据库添加 is_admin 列（如果没有的话）
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass  # 列已存在
    
    # 确保大力猪是管理员
    cursor.execute('UPDATE users SET is_admin = 1 WHERE username = ?', ('大力猪',))
    conn.commit()
    
    # 爬墙记录表 - 统一使用旧版字段名
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            gym TEXT NOT NULL,
            routes TEXT,
            type TEXT,
            duration REAL,
            partners TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 岩馆配置表迁移：旧表有user_id，新表全局共享
    cursor.execute("PRAGMA table_info(gyms)")
    gym_cols = [r[1] for r in cursor.fetchall()]
    if 'user_id' in gym_cols:
        # 需要迁移：旧表有user_id列
        cursor.execute('ALTER TABLE gyms RENAME TO gyms_old')
        cursor.execute('''
            CREATE TABLE gyms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gym_name TEXT NOT NULL,
                wall_type TEXT
            )
        ''')
        cursor.execute('INSERT INTO gyms (gym_name, wall_type) SELECT gym_name, wall_type FROM gyms_old')
        cursor.execute('DROP TABLE gyms_old')
        print('已将gyms表迁移为全局共享模式')
    
    # 搭子配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 用户设置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            max_grade TEXT DEFAULT 'V6'
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"数据库初始化完成: {DATABASE_PATH}")

if __name__ == '__main__':
    init_database()
