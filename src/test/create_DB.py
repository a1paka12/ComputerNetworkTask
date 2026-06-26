import sqlite3
import random
import os

# 1. DB 연결 및 파일 생성 (현재 작업 폴더에 생성)
db_path = 'ecommerce.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 2. 기존 테이블이 있다면 삭제 (초기화)
cursor.execute('DROP TABLE IF EXISTS products')

# 3. 테이블 생성
cursor.execute('''
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    price INTEGER NOT NULL,
    stock INTEGER NOT NULL
)
''')

# 4. 더미 데이터 1000개 생성
categories = ['Electronics', 'Books', 'Clothing', 'Home_Appliances', 'Sports']
adjectives = ['Premium', 'Basic', 'Smart', 'Wireless', 'Portable', 'Classic', 'Eco-friendly', 'Advanced']
nouns = ['Device', 'Widget', 'Monitor', 'Tool', 'Gear', 'Apparel', 'Kit', 'System']

data_to_insert = []
for i in range(1000):
    name = f"{random.choice(adjectives)} {random.choice(nouns)} {i+1}"
    category = random.choice(categories)
    price = random.randint(1, 200) * 500  # 500원 ~ 100,000원
    stock = random.randint(0, 100)
    data_to_insert.append((name, category, price, stock))

# 5. DB에 일괄 삽입 및 저장(commit) -> 이 부분이 가장 중요합니다!
cursor.executemany(
    'INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)', 
    data_to_insert
)
conn.commit() # 실제 파일에 데이터를 쓰는 명령어

# 6. 정상적으로 들어갔는지 확인
cursor.execute('SELECT COUNT(*) FROM products')
count = cursor.fetchone()[0]

print(f"데이터베이스 생성 완료! (경로: {os.path.abspath(db_path)})")
print(f"'products' 테이블에 총 {count}개의 데이터가 삽입되었습니다.\n")

print("[샘플 데이터 3개 확인]")
cursor.execute('SELECT * FROM products LIMIT 3')
for row in cursor.fetchall():
    print(row)

conn.close()