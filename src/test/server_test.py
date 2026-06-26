import sqlite3

# DB 연결 및 파일 생성 (코랩의 현재 작업 디렉토리에 생성됨)
db_path = 'ecommerce.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 변경사항 저장 및 확인
conn.commit()
cursor.execute('SELECT COUNT(*) FROM products')
count = cursor.fetchone()[0]

print(f"파일명: {db_path}")
print(f"'products' 테이블에 총 {count}개")

# 샘플 데이터 3개 출력
print("\n샘플 데이터 확인")
cursor.execute('select * from products limit 3')
for row in cursor.fetchall():
    print(row)

conn.close()