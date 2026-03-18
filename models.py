# -*- coding: utf-8 -*-
"""
数据模型
定义用户、爬墙记录、岩馆、搭子等数据模型
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data', 'climbing.db')

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

# ==================== 用户模型 ====================

def create_user(username, password):
    """创建新用户"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, hash_password(password))
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None  # 用户名已存在
    finally:
        conn.close()

def verify_user(username, password):
    """验证用户登录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, username FROM users WHERE username = ? AND password = ?',
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """根据ID获取用户"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

# ==================== 爬墙记录模型 ====================

def add_record(user_id, date, gym, routes=None, type=None, duration=None, partners=None, notes=None):
    """添加爬墙记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO records (user_id, date, gym, routes, type, duration, partners, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, date, gym, routes, type, duration, partners, notes))
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id

def get_records(user_id):
    """获取用户所有爬墙记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM records WHERE user_id = ? ORDER BY date DESC, created_at DESC
    ''', (user_id,))
    records = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return records

def update_record(record_id, user_id, date=None, gym=None, routes=None, type=None, duration=None, partners=None, notes=None):
    """更新爬墙记录"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 先查询现有记录
    cursor.execute('SELECT * FROM records WHERE id = ? AND user_id = ?', (record_id, user_id))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        return False
    
    # 更新字段
    cursor.execute('''
        UPDATE records 
        SET date = ?, gym = ?, routes = ?, type = ?, duration = ?, partners = ?, notes = ?
        WHERE id = ? AND user_id = ?
    ''', (
        date or existing['date'],
        gym or existing['gym'],
        routes if routes is not None else existing['routes'],
        type or existing['type'],
        duration if duration is not None else existing['duration'],
        partners or existing['partners'],
        notes or existing['notes'],
        record_id, user_id
    ))
    conn.commit()
    conn.close()
    return True

def delete_record(record_id, user_id):
    """删除爬墙记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM records WHERE id = ? AND user_id = ?', (record_id, user_id))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def clear_all_records(user_id):
    """清空用户所有记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM records WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# ==================== 岩馆模型 ====================

def add_gym(user_id, gym_name, wall_type=None):
    """添加岩馆"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO gyms (user_id, gym_name, wall_type) VALUES (?, ?, ?)',
        (user_id, gym_name, wall_type)
    )
    conn.commit()
    conn.close()

def get_gyms(user_id):
    """获取用户岩馆列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM gyms WHERE user_id = ?', (user_id,))
    gyms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return gyms

def delete_gym(gym_id, user_id):
    """删除岩馆"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gyms WHERE id = ? AND user_id = ?', (gym_id, user_id))
    conn.commit()
    conn.close()

def clear_all_gyms(user_id):
    """清空用户所有岩馆"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gyms WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def clear_all_partners(user_id):
    """清空用户所有搭子"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM partners WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

# ==================== 搭子模型 ====================

def add_partner(user_id, name):
    """添加搭子"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO partners (user_id, name) VALUES (?, ?)',
        (user_id, name)
    )
    conn.commit()
    conn.close()

def get_partners(user_id):
    """获取用户搭子列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM partners WHERE user_id = ?', (user_id,))
    partners = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return partners

def delete_partner(partner_id, user_id):
    """删除搭子"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM partners WHERE id = ? AND user_id = ?', (partner_id, user_id))
    conn.commit()
    conn.close()

# ==================== 数据导入导出 ====================

def export_user_data(user_id):
    """导出用户所有数据"""
    return {
        'records': get_records(user_id),
        'gyms': get_gyms(user_id),
        'partners': get_partners(user_id),
        'exported_at': datetime.now().isoformat()
    }

def import_user_data(user_id, data):
    """导入用户数据 - 使用旧版字段名"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 导入记录
    if 'records' in data:
        for record in data['records']:
            routes = record.get('routes') or record.get('grade', '')
            if isinstance(routes, list):
                routes = ', '.join(str(x) for x in routes)
            type_val = record.get('type') or record.get('result', '')
            if isinstance(type_val, list):
                type_val = ', '.join(str(x) for x in type_val)
            duration = record.get('duration')
            partners = record.get('partners') or record.get('partner', '')
            if isinstance(partners, list):
                partners = ', '.join(str(x) for x in partners)
            notes = record.get('notes') or record.get('note', '')
            if isinstance(notes, dict):
                notes = str(notes)
            
            cursor.execute('''
                INSERT INTO records (user_id, date, gym, routes, type, duration, partners, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, record['date'], record['gym'], str(routes) if routes else None, str(type_val) if type_val else None, duration, str(partners) if partners else None, str(notes) if notes else None))
    
    # 导入岩馆 - 支持新旧格式
    if 'settings' in data and 'gyms' in data['settings']:
        # 旧格式: settings.gyms 是 {category: [gym names]}
        for category, gym_list in data['settings']['gyms'].items():
            for gym_name in gym_list:
                cursor.execute(
                    'INSERT INTO gyms (user_id, gym_name, wall_type) VALUES (?, ?, ?)',
                    (user_id, gym_name, category)
                )
    elif 'gyms' in data:
        # 新格式: gyms 是 [{gym_name, wall_type}]
        for gym in data['gyms']:
            cursor.execute(
                'INSERT INTO gyms (user_id, gym_name, wall_type) VALUES (?, ?, ?)',
                (user_id, gym.get('gym_name'), gym.get('wall_type'))
            )
    
    # 导入搭子 - 支持新旧格式
    if 'settings' in data and 'partners' in data['settings']:
        # 旧格式: settings.partners 是 [names]
        for name in data['settings']['partners']:
            cursor.execute(
                'INSERT INTO partners (user_id, name) VALUES (?, ?)',
                (user_id, name)
            )
    elif 'partners' in data:
        # 新格式: partners 是 [{name}]
        for partner in data['partners']:
            cursor.execute(
                'INSERT INTO partners (user_id, name) VALUES (?, ?)',
                (user_id, partner.get('name'))
            )
    
    conn.commit()
    conn.close()
