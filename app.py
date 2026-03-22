# -*- coding: utf-8 -*-
"""
抱石日历 Flask 后端主程序
"""

from flask import Flask, request, jsonify, session
import os
import json

from models import (
    create_user, verify_user, get_user_by_id,
    add_record, get_records, update_record, delete_record, clear_all_records,
    add_gym, get_gyms, delete_gym, delete_gym_by_name, clear_all_gyms,
    add_partner, get_partners, delete_partner, delete_partner_by_name,
    export_user_data, import_user_data,
    get_max_grade, save_max_grade
)

app = Flask(__name__)
app.secret_key = 'climbing-calendar-secret-key-2026'

# 确保数据库存在
from database import init_database
init_database()

# ==================== 辅助函数 ====================

def get_current_user_id():
    """获取当前登录用户ID"""
    return session.get('user_id')

def require_login(f):
    """登录装饰器"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_current_user_id():
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated

# ==================== 用户认证接口 ====================

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'})
    
    user_id = create_user(username, password)
    if user_id:
        session['user_id'] = user_id
        session['username'] = username
        return jsonify({'success': True, 'message': '注册成功'})
    else:
        return jsonify({'error': '用户名已存在'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = verify_user(username, password)
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['is_admin'] = user.get('is_admin', 0)
        return jsonify({'success': True, 'username': user['username'], 'is_admin': user.get('is_admin', 0)})
    else:
        return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check_login', methods=['GET'])
def check_login():
    """检查登录状态"""
    user_id = get_current_user_id()
    if user_id:
        user = get_user_by_id(user_id)
        return jsonify({'logged_in': True, 'username': user['username'], 'is_admin': user.get('is_admin', 0)})
    return jsonify({'logged_in': False})

# ==================== 爬墙记录接口 ====================

@app.route('/api/records', methods=['GET'])
@require_login
def get_records_api():
    """获取当前用户所有记录"""
    user_id = get_current_user_id()
    records = get_records(user_id)
    return jsonify(records)

@app.route('/api/records', methods=['POST'])
@require_login
def add_record_api():
    """添加新记录"""
    user_id = get_current_user_id()
    data = request.json
    
    record_id = add_record(
        user_id=user_id,
        date=data.get('date'),
        gym=data.get('gym'),
        routes=data.get('routes'),
        type=data.get('type'),
        duration=data.get('duration'),
        partners=data.get('partners'),
        notes=data.get('notes')
    )
    return jsonify({'success': True, 'id': record_id})

@app.route('/api/records/<int:record_id>', methods=['PUT'])
@require_login
def update_record_api(record_id):
    """更新记录"""
    user_id = get_current_user_id()
    data = request.json
    
    success = update_record(
        record_id=record_id,
        user_id=user_id,
        date=data.get('date'),
        gym=data.get('gym'),
        routes=data.get('routes'),
        type=data.get('type'),
        duration=data.get('duration'),
        partners=data.get('partners'),
        notes=data.get('notes')
    )
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '记录不存在'}), 404

@app.route('/api/records/<int:record_id>', methods=['DELETE'])
@require_login
def delete_record_api(record_id):
    """删除记录"""
    user_id = get_current_user_id()
    success = delete_record(record_id, user_id)
    if success:
        return jsonify({'success': True})
    return jsonify({'error': '记录不存在'}), 404

@app.route('/api/records/clear', methods=['POST'])
@require_login
def clear_records_api():
    """清空所有记录"""
    user_id = get_current_user_id()
    clear_all_records(user_id)
    return jsonify({'success': True})

# ==================== 岩馆配置接口 ====================

@app.route('/api/gyms', methods=['GET'])
@require_login
def get_gyms_api():
    """获取岩馆列表（全局共享）"""
    gyms = get_gyms(None)
    return jsonify(gyms)

@app.route('/api/gyms', methods=['POST'])
@require_login
def add_gym_api():
    """添加岩馆 - 仅管理员"""
    if not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    data = request.json
    add_gym(None, data.get('gym_name'), data.get('wall_type'))
    return jsonify({'success': True})

@app.route('/api/gyms/clear', methods=['POST'])
@require_login
def clear_gyms_api():
    """清空所有岩馆 - 仅管理员"""
    if not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    clear_all_gyms()
    return jsonify({'success': True})

@app.route('/api/gyms/<int:gym_id>', methods=['DELETE'])
@require_login
def delete_gym_api(gym_id):
    """删除岩馆 - 仅管理员"""
    if not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    delete_gym(gym_id)
    return jsonify({'success': True})

@app.route('/api/gyms/delete', methods=['POST'])
@require_login
def delete_gym_by_name_api():
    """按名称删除岩馆 - 仅管理员"""
    if not session.get('is_admin'):
        return jsonify({'error': '无权限'}), 403
    data = request.json or {}
    name = data.get('name')
    wall_type = data.get('wall_type')
    if not name:
        return jsonify({'error': '缺少参数'}), 400
    delete_gym_by_name(name, wall_type)
    return jsonify({'success': True})

# ==================== 搭子配置接口 ====================

@app.route('/api/partners', methods=['GET'])
@require_login
def get_partners_api():
    """获取搭子列表"""
    user_id = get_current_user_id()
    partners = get_partners(user_id)
    return jsonify(partners)

@app.route('/api/partners', methods=['POST'])
@require_login
def add_partner_api():
    """添加搭子"""
    user_id = get_current_user_id()
    data = request.json
    add_partner(user_id, data.get('name'))
    return jsonify({'success': True})

@app.route('/api/partners/<int:partner_id>', methods=['DELETE'])
@require_login
def delete_partner_api(partner_id):
    """删除搭子"""
    user_id = get_current_user_id()
    delete_partner(partner_id, user_id)
    return jsonify({'success': True})

@app.route('/api/partners/delete', methods=['POST'])
@require_login
def delete_partner_by_name_api():
    """按名称删除搭子"""
    user_id = get_current_user_id()
    data = request.json or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': '缺少参数'}), 400
    delete_partner_by_name(name, user_id)
    return jsonify({'success': True})

@app.route('/api/partners/clear', methods=['POST'])
@require_login
def clear_partners_api():
    """清空所有搭子"""
    user_id = get_current_user_id()
    clear_all_partners(user_id)
    return jsonify({'success': True})

# ==================== 数据导入导出接口 ====================

@app.route('/api/export', methods=['GET'])
@require_login
def export_data_api():
    """导出用户数据"""
    user_id = get_current_user_id()
    data = export_user_data(user_id)
    # 非管理员不导出岩馆
    if not session.get('is_admin'):
        data.pop('gyms', None)
    return jsonify(data)

@app.route('/api/import', methods=['POST'])
@require_login
def import_data_api():
    """导入用户数据"""
    user_id = get_current_user_id()
    is_admin = session.get('is_admin', 0)
    data = request.json
    try:
        import_user_data(user_id, data, is_admin)
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/settings/max_grade', methods=['POST'])
@require_login
def save_max_grade_api():
    """保存最高级别"""
    user_id = get_current_user_id()
    data = request.json
    grade = data.get('grade', '')
    save_max_grade(user_id, grade)
    return jsonify({'success': True})

@app.route('/api/settings/max_grade', methods=['GET'])
@require_login
def get_max_grade_api():
    """获取最高级别"""
    user_id = get_current_user_id()
    grade = get_max_grade(user_id)
    return jsonify({'grade': grade})

# ==================== 前端页面 ====================

@app.route('/')
def index():
    """登录页面"""
    return app.send_static_file('login.html')

@app.route('/login.html')
def login_page():
    """登录页面（兼容）"""
    return app.send_static_file('login.html')

@app.route('/calendar.html')
def calendar():
    """主页面"""
    return app.send_static_file('calendar.html')

# ==================== 意见反馈接口 ====================

@app.route('/api/feedback', methods=['POST'])
@require_login
def feedback_api():
    """处理意见反馈"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from email.mime.image import MIMEImage
    import uuid
    
    user_id = get_current_user_id()
    user = get_user_by_id(user_id)
    username = user.get('username', '用户') if user else '用户'
    
    text = request.form.get('text', '')
    
    # 发送邮件
    smtp_server = 'smtp.qq.com'
    smtp_port = 465
    sender = '709497698@qq.com'
    password = 'hibisvbooxwnbbbb'
    receiver = '709497698@qq.com'
    
    msg = MIMEMultipart('related')
    msg['Subject'] = f'《意见反馈-【{username}】》'
    msg['From'] = sender
    msg['To'] = receiver
    
    # 添加正文
    html_body = f'''
    <html>
    <body>
        <h2>💬 意见反馈</h2>
        <p><strong>用户名：</strong>{username}</p>
        <p><strong>反馈内容：</strong></p>
        <p>{text}</p>
    </body>
    </html>
    '''
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))
    
    # 处理图片附件
    files = request.files.getlist('images')
    for i, file in enumerate(files):
        if file:
            img_data = file.read()
            img_name = f'image_{i}_{file.filename}'
            img = MIMEImage(img_data)
            img.add_header('Content-Disposition', f'attachment; filename={img_name}')
            msg.attach(img)
    
    try:
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
