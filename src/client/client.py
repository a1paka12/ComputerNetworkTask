import tkinter as tk
from tkinter import ttk, messagebox
import socket
import hashlib
import json

class AdvancedInventoryClient:
    def __init__(self, root):
        self.root = root
        self.root.title("재고 관리 시스템")
        self.root.geometry("700x500")
        
        # 화면(Frame) 관리를 위한 딕셔너리
        self.frames = {}
        
        # 3개의 주요 화면 생성
        self.create_login_frame()
        self.create_admin_frame()
        self.create_staff_frame()
        
        # 앱 시작 시 로그인 화면 띄우기
        self.show_frame("login")

    # ==========================================
    # 통신 모듈 (HTTP Socket)
    # ==========================================
    def send_http_request(self, method, uri, payload=None):
        host = '127.0.0.1'
        port = 80
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            
            # HTTP Request 조립
            request = f"{method} {uri} HTTP/1.1\r\n"
            request += f"Host: {host}:{port}\r\n"
            request += "Content-Type: application/json\r\n"
            
            body = ""
            if payload:
                body = json.dumps(payload)
                request += f"Content-Length: {len(body)}\r\n"
                
            request += "Connection: close\r\n\r\n"
            request += body
            
            client_socket.sendall(request.encode('utf-8'))
            
            # 응답 수신
            response_data = b""
            while True:
                chunk = client_socket.recv(4096)
                if not chunk: break
                response_data += chunk
                
            client_socket.close()
            return response_data.decode('utf-8')
            
        except Exception as e:
            return f"HTTP/1.1 500 ERROR\r\n\r\n{e}"

    # ==========================================
    # 화면 전환 로직
    # ==========================================
    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget() # 모든 화면 숨기기
        self.frames[frame_name].pack(fill="both", expand=True) # 선택한 화면만 보이기

    # ==========================================
    # 1. 로그인 화면 구성
    # ==========================================
    def create_login_frame(self):
        frame = tk.Frame(self.root, pady=100)
        self.frames["login"] = frame
        
        tk.Label(frame, text="시스템 로그인", font=("Arial", 20, "bold")).pack(pady=20)
        
        # ID 입력
        frame_id = tk.Frame(frame)
        frame_id.pack(pady=5)
        tk.Label(frame_id, text="아이디:", width=10).pack(side="left")
        self.entry_id = tk.Entry(frame_id)
        self.entry_id.pack(side="left")
        
        # 비밀번호 입력 (show="*" 로 가림 처리)
        frame_pw = tk.Frame(frame)
        frame_pw.pack(pady=5)
        tk.Label(frame_pw, text="비밀번호:", width=10).pack(side="left")
        self.entry_pw = tk.Entry(frame_pw, show="*")
        self.entry_pw.pack(side="left")
        
        # 로그인 버튼
        tk.Button(frame, text="로그인", width=20, bg="#4CAF50", fg="black", command=self.attempt_login).pack(pady=20)

    def attempt_login(self):
        user_id = self.entry_id.get().strip()
        user_pw = self.entry_pw.get().strip()
        
        if not user_id or not user_pw:
            messagebox.showwarning("경고", "아이디와 비밀번호를 모두 입력하세요.")
            return

        # [임시 로직] 아직 서버가 없으므로 클라이언트 단에서 더미 테스트 진행
        # 나중에는 C++ 서버로 POST /login 요청을 보내고 200/401 응답을 파싱하여 처리합니다.
        if user_id == "admin" and user_pw == "1234":
            messagebox.showinfo("성공", "관리자님 환영합니다.")
            self.show_frame("admin")
        elif user_id == "staff1" and user_pw == "1111":
            messagebox.showinfo("성공", "직원님 환영합니다.")
            self.show_frame("staff")
        else:
            messagebox.showerror("실패", "아이디 또는 비밀번호가 틀렸습니다. (401 Unauthorized)")

    # ==========================================
    # 2. 관리자(Admin) 화면 구성
    # ==========================================
    def create_admin_frame(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        self.frames["admin"] = frame
        
        # 상단 메뉴바
        header = tk.Frame(frame)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="관리자 대시보드", font=("Arial", 16, "bold")).pack(side="left")
        tk.Button(header, text="로그아웃", command=lambda: self.show_frame("login")).pack(side="right")

        # 컨트롤 패널
        control_panel = tk.Frame(frame)
        control_panel.pack(fill="x", pady=5)
        tk.Button(control_panel, text="전체 재고 조회", width=15).pack(side="left", padx=5)
        tk.Button(control_panel, text="상품 정보 수정", width=15).pack(side="left", padx=5)
        tk.Button(control_panel, text="통계 보기", width=15).pack(side="left", padx=5)
        
        # 표 (Treeview) 생성
        columns = ("id", "name", "price", "stock")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        tree.heading("id", text="ID")
        tree.heading("name", text="상품명")
        tree.heading("price", text="가격(원)")
        tree.heading("stock", text="재고(개)")
        
        tree.column("id", width=50, anchor="center")
        tree.column("name", width=250, anchor="w")
        tree.column("price", width=100, anchor="e")
        tree.column("stock", width=100, anchor="e")
        tree.pack(fill="both", expand=True)

    # ==========================================
    # 3. 직원(Staff) 화면 구성
    # ==========================================
    def create_staff_frame(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        self.frames["staff"] = frame
        
        header = tk.Frame(frame)
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="직원 재고 관리", font=("Arial", 16, "bold")).pack(side="left")
        tk.Button(header, text="로그아웃", command=lambda: self.show_frame("login")).pack(side="right")

        control_panel = tk.Frame(frame)
        control_panel.pack(fill="x", pady=5)
        tk.Button(control_panel, text="재고 조회", width=15).pack(side="left", padx=5)
        tk.Button(control_panel, text="판매 처리 (재고 차감)", width=20, bg="#ff9800").pack(side="left", padx=5)

        # 표 (Treeview) 생성
        columns = ("id", "name", "price", "stock")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        tree.heading("id", text="ID")
        tree.heading("name", text="상품명")
        tree.heading("price", text="가격")
        tree.heading("stock", text="현재 재고")
        tree.pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    
    # 맥북 강제 최상단 노출
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    app = AdvancedInventoryClient(root)
    root.mainloop()