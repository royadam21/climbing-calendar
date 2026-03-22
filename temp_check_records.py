# -*- coding: utf-8 -*-
from database import get_records, init_database, get_user_by_username

init_database()

# 查找大力猪
user = get_user_by_username('大力猪')
print('大力猪用户:', user)

# 获取记录
user_id = user['id'] if user else 1
records = get_records(user_id)
print('记录数量:', len(records))
for r in records[:10]:
    print(r)
