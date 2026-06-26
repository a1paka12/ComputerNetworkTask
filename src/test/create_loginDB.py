import sqlite3
import hashlib

# 1. 비밀번호 해싱 함수 (SHA-256 알고리즘 사용)
def hash_password(password):
    # 비밀번호 문자열을 바이트로 변환한 뒤 해싱하고, 다시 16진수 문자열로 반환합니다.
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# 2. DB 연결 (기존 상품 DB 파일에 테이블을 추가합니다)
db_path = 'ecommerce.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 3. 기존 users 테이블이 있다면 삭제 (초기화 목적)
cursor.execute('DROP TABLE IF EXISTS users')

# 4. users 테이블 생성
# role: 'admin' (관리자) 또는 'staff' (직원)
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

# 5. 초기 계정 데이터 셋업 (비밀번호는 해싱 함수를 통과시켜 저장)
# 기획하신 대로 관리자 1명, 직원 2명을 생성합니다.
users_data = [
    ('admin', hash_password('1234'), 'admin'),
    ('staff1', hash_password('1111'), 'staff'),
    ('staff2', hash_password('2222'), 'staff')
]

# 6. DB에 일괄 삽입 및 저장
cursor.executemany(
    'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', 
    users_data
)
conn.commit()

# 7. 정상적으로 들어갔는지 확인 출력
print(f"사용자 DB 테이블(users) 생성 완료! (경로: {db_path})\n")
print("--- 등록된 계정 목록 ---")

cursor.execute('SELECT id, username, password_hash, role FROM users')
for row in cursor.fetchall():
    user_id = row[0]
    username = row[1]
    pw_hash = row[2]
    role = row[3]
    # 해시값은 너무 길어서 앞의 15자리만 잘라서 보여줍니다.
    print(f"[{role.upper()}] 아이디: {username} | 암호화된 PW: {pw_hash[:15]}... | 내부ID: {user_id}")

conn.close()