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

def create_user(username, password, is_admin=0):
    """创建新用户"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, is_admin, created_at) VALUES (?, ?, ?, datetime('now', 'localtime'))",
            (username, hash_password(password), is_admin)
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
        'SELECT id, username, is_admin FROM users WHERE username = ? AND password = ?',
        (username, hash_password(password))
    )
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    """根据ID获取用户"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, is_admin, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None
    return dict(user) if user else None

# ==================== 爬墙记录模型 ====================

def add_record(user_id, date, gym, routes=None, type=None, duration=None, partners=None, notes=None):
    """添加爬墙记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO records (user_id, date, gym, routes, type, duration, partners, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
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
    """添加岩馆（全局，无用户区分）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO gyms (gym_name, wall_type) VALUES (?, ?)',
        (gym_name, wall_type)
    )
    conn.commit()
    conn.close()

def get_gyms(user_id):
    """获取岩馆列表（全局，所有用户共享）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, gym_name, wall_type FROM gyms ORDER BY id')
    gyms = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return gyms

def delete_gym(gym_id):
    """删除岩馆（全局）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gyms WHERE id = ?', (gym_id,))
    conn.commit()
    conn.close()

def delete_gym_by_name(gym_name, wall_type=None):
    """按名称删除岩馆（全局）"""
    conn = get_db()
    cursor = conn.cursor()
    if wall_type:
        cursor.execute('DELETE FROM gyms WHERE gym_name = ? AND wall_type = ?', (gym_name, wall_type))
    else:
        cursor.execute('DELETE FROM gyms WHERE gym_name = ?', (gym_name,))
    conn.commit()
    conn.close()

def clear_all_gyms():
    """清空所有岩馆（全局）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM gyms')
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

def delete_partner_by_name(name, user_id):
    """按名称删除搭子"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM partners WHERE name = ? AND user_id = ?', (name, user_id))
    conn.commit()
    conn.close()

# ==================== 用户设置 ====================

def get_max_grade(user_id):
    """获取用户最高级别"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT max_grade FROM user_settings WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)['max_grade'] if isinstance(row, sqlite3.Row) else row[0]
        return 'V6'
    except Exception:
        conn.close()
        return 'V6'

def save_max_grade(user_id, grade):
    """保存用户最高级别"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO user_settings (user_id, max_grade) VALUES (?, ?)', (user_id, grade))
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

def import_user_data(user_id, data, is_admin=0):
    """导入用户数据 - 全删全插"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 先清空现有数据
    cursor.execute('DELETE FROM records WHERE user_id = ?', (user_id,))
    # 岩馆是全局的，只有管理员导入时才清空岩馆
    if is_admin:
        cursor.execute('DELETE FROM gyms')
    cursor.execute('DELETE FROM partners WHERE user_id = ?', (user_id,))
    
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
                INSERT INTO records (user_id, date, gym, routes, type, duration, partners, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
            ''', (user_id, record['date'], record['gym'], str(routes) if routes else None, str(type_val) if type_val else None, duration, str(partners) if partners else None, str(notes) if notes else None))
    
    # 导入岩馆 - 支持新旧格式（岩馆是全局的，无user_id）
    if 'settings' in data and 'gyms' in data['settings']:
        # 旧格式: settings.gyms 是 {category: [gym names]}
        for category, gym_list in data['settings']['gyms'].items():
            for gym_name in gym_list:
                cursor.execute(
                    'INSERT INTO gyms (gym_name, wall_type) VALUES (?, ?)',
                    (gym_name, category)
                )
    elif 'gyms' in data:
        # 新格式: gyms 是 [{gym_name, wall_type}]，岩馆是全局的
        for gym in data['gyms']:
            cursor.execute(
                'INSERT INTO gyms (gym_name, wall_type) VALUES (?, ?)',
                (gym.get('gym_name'), gym.get('wall_type'))
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

# ==================== 登录日志模块 ====================

def add_login_log(user_id, username, ip_address=None, user_agent=None, success=1):
    """记录登录日志"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 使用本地时间存储，不用 CURRENT_TIMESTAMP（UTC时间）
        cursor.execute(
            "INSERT INTO login_logs (user_id, username, ip_address, user_agent, success, login_time) VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))",
            (user_id, username, ip_address, user_agent, success)
        )
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"添加登录日志失败: {e}")
        return None
    finally:
        conn.close()

def get_login_logs(limit=100):
    """获取登录日志"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM login_logs ORDER BY login_time DESC LIMIT ?', (limit,))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs

def get_login_logs_by_user(user_id, limit=50):
    """获取指定用户的登录日志"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM login_logs WHERE user_id = ? ORDER BY login_time DESC LIMIT ?', (user_id, limit))
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return logs
