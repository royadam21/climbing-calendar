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
    
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    
    # 岩馆配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gyms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            gym_name TEXT NOT NULL,
            wall_type TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # 搭子配置表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"数据库初始化完成: {DATABASE_PATH}")

if __name__ == '__main__':
    init_database()
