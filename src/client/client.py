import tkinter as tk
from tkinter import ttk, messagebox
import socket
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

    
    # 통신 모듈 (HTTP Socket)
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

    # 화면 전환 로직
    def show_frame(self, frame_name):
        for frame in self.frames.values():
            frame.pack_forget() # 모든 화면 숨기기
        self.frames[frame_name].pack(fill="both", expand=True) # 선택한 화면만 보이기

    
    # 로그인 화면 구성
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
        tk.Button(frame, text="로그인", width=20, bg="#4CAF50", fg="black", command=self.on_login_click).pack(pady=20)
    
    def on_login_click(self):
        # 사용자가 입력한 ID와 PW를 가져옴.
        input_id = self.entry_id.get()
        input_pw = self.entry_pw.get()
        
        # 통신 함수를 호출하여 로그인을 시도
        success, result = self.attempt_login(input_id, input_pw)
        
        # 결과에 따른 화면 전환 처리
        if success:
            role = result # 'admin' 또는 'staff'
            messagebox.showinfo("로그인 성공", f"환영합니다! ({role} 권한)")
            
            # 서버가 넘겨준 권한 문자열을 그대로 사용해서 화면을 전환
            if role == "admin":
                self.show_frame("admin")
            else:
                self.show_frame("staff")
                
            # 로그인 창에 남아있는 글자 지우기
            self.entry_id.delete(0, 'end')
            self.entry_pw.delete(0, 'end')
            
        else:
            # 실패 시 에러 메시지 팝업
            messagebox.showerror("로그인 실패", result)
    
    def attempt_login(self, user_id, user_pw):
        """
        서버(80 포트)로 ID와 PW를 보내서 로그인
        """
        host = '127.0.0.1'
        port = 80
        
        # 서버가 파싱하기 좋게 JSON 형태의 문자열 생성
        body_str = f'{{"id": "{user_id}", "pw": "{user_pw}"}}'
        
        # HTTP POST 요청 메시지
        request_msg = (
            f"POST /login HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {len(body_str.encode('utf-8'))}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
            f"{body_str}"
        )
        
        try:
            # 서버에 소켓 연결 및 데이터 전송
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3.0)  # 3초 안에 응답 없으면 타임아웃
                s.connect((host, port))
                s.sendall(request_msg.encode('utf-8'))
                
                # 서버로부터 응답 수신
                response_data = s.recv(4096).decode('utf-8')
                
                # 응답 파싱
                if '\r\n\r\n' in response_data:
                    headers, res_body = response_data.split('\r\n\r\n', 1)
                else:
                    return False, "서버 응답 형식이 올바르지 않습니다."

                # HTTP 상태 코드 확인 (예: "HTTP/1.1 200 OK")
                status_line = headers.split('\n')[0]
                
                # 결과 처리 (서버가 던진 200 또는 401 분석)
                if " 200 " in status_line:
                    # 로그인 성공 시 JSON 바디에서 권한(role) 추출
                    res_json = json.loads(res_body)
                    role = res_json.get("role", "staff")
                    return True, role
                    
                elif " 401 " in status_line:
                    return False, "아이디 또는 비밀번호가 일치하지 않습니다."
                else:
                    return False, f"서버 에러 발생: {status_line}"
                    
        except ConnectionRefusedError:
            return False, "서버에 연결할 수 없습니다. (C++ 서버가 켜져 있는지 확인하세요!)"
        except Exception as e:
            return False, f"알 수 없는 통신 오류: {e}"
    
    # api request method
    def send_api_request(self, method, uri, payload=None):
        host = '127.0.0.1'
        port = 80
        
        request = f"{method} {uri} HTTP/1.1\r\n"
        request += f"Host: {host}:{port}\r\n"
        request += "Content-Type: application/json\r\n"
        
        body_str = ""
        if payload:
            body_str = json.dumps(payload)
            request += f"Content-Length: {len(body_str.encode('utf-8'))}\r\n"
            
        request += "Connection: close\r\n\r\n"
        request += body_str
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(3.0)
                s.connect((host, port))
                s.sendall(request.encode('utf-8'))
                
                # 4096바이트씩 계속 쪼개서 끝까지 다 받습니다.
                response_bytes = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk: # 서버가 다 보내고 연결을 끊으면 탈출
                        break
                    response_bytes += chunk
                
                # 끝까지 다 받은 데이터를 한 번에 문자열로 변환
                response_data = response_bytes.decode('utf-8')
                
                if '\r\n\r\n' in response_data:
                    headers, body = response_data.split('\r\n\r\n', 1)
                    status_code = int(headers.split(' ')[1])
                    return status_code, body
                return 500, "Invalid Response Format"
        except Exception as e:
            return 500, str(e)
        
    def refresh_admin_data(self):
        """GET /products 요청을 보내서 표를 갱신."""
        status, body = self.send_api_request("GET", "/products")
        
        if status == 200:
            try:
                # JSON 변환 시도
                products = json.loads(body)
                
                # 기존 데이터 싹 지우기
                for item in self.tree.get_children():
                    self.tree.delete(item)
                    
                # 새 데이터 채워넣기
                for p in products:
                    self.tree.insert("", "end", values=(p['id'], p['name'], p['price'], p['stock']))
                
            except json.JSONDecodeError as e:
                # JSON 형식이 깨져서 파이썬이 못 읽을 때 팝업을 띄웁니다.
                messagebox.showerror("JSON 해독 에러", f"서버가 이상한 데이터를 보냈습니다.\n에러: {e}\n원본: {body}")
        else:
            messagebox.showerror("조회 실패", f"데이터를 불러오지 못했습니다.\n코드: {status}\n내용: {body}")

    def delete_product(self):
        """DELETE /products/{id} 요청."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "삭제할 상품을 먼저 선택해주세요.")
            return
            
        item_values = self.tree.item(selected[0])['values']
        product_id = item_values[0]
        product_name = item_values[1]
        
        if messagebox.askyesno("삭제 확인", f"'{product_name}' 상품을 정말 삭제하시겠습니까?"):
            status, body = self.send_api_request("DELETE", f"/products/{product_id}")
            if status == 200:
                self.refresh_admin_data() # 삭제 성공 시 즉시 새로고침
                messagebox.showinfo("성공", "삭제되었습니다.")
            else:
                messagebox.showerror("실패", f"삭제 실패: {body}")

    def show_add_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("상품 추가")
        popup.geometry("300x200")
        
        tk.Label(popup, text="상품명").pack(pady=2)
        name_entry = tk.Entry(popup)
        name_entry.pack(pady=2)

        tk.Label(popup, text="카테고리").pack(pady=2)
        category_list = ['Electronics', 'Books', 'Clothing', 'Home_Appliances', 'Sports', '일반']
        category_combo = ttk.Combobox(popup, values=category_list, state="readonly")
        category_combo.current(0)
        category_combo.pack(pady=2)
        
        tk.Label(popup, text="가격").pack(pady=2)
        price_entry = tk.Entry(popup)
        price_entry.pack(pady=2)
        
        tk.Label(popup, text="재고").pack(pady=2)
        stock_entry = tk.Entry(popup)
        stock_entry.pack(pady=2)
        
        def on_submit():
            payload = {
                "name": name_entry.get(),
                "category": category_combo.get(),
                "price": str(price_entry.get() or 0),
                "stock": str(stock_entry.get() or 0)
            }
            status, body = self.send_api_request("POST", "/products", payload)
            if status == 201 or status == 200:
                popup.destroy()
                self.refresh_admin_data() # 추가 성공 시 표 새로고침
            else:
                messagebox.showerror("실패", body)
                
        tk.Button(popup, text="저장", command=on_submit).pack(pady=10)

    def show_edit_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("경고", "수정할 상품을 선택해주세요.")
            return
            
        item_values = self.tree.item(selected[0])['values']
        product_id = item_values[0]
        
        popup = tk.Toplevel(self.root)
        popup.title("상품 수정")
        popup.geometry("300x200")
        
        tk.Label(popup, text="상품명").pack()
        name_entry = tk.Entry(popup)
        name_entry.insert(0, item_values[1])
        name_entry.pack()
        
        tk.Label(popup, text="가격").pack()
        price_entry = tk.Entry(popup)
        price_entry.insert(0, item_values[2])
        price_entry.pack()
        
        tk.Label(popup, text="재고").pack()
        stock_entry = tk.Entry(popup)
        stock_entry.insert(0, item_values[3])
        stock_entry.pack()
        
        def on_submit():
            payload = {
                "name": name_entry.get(),
                "price": str(price_entry.get() or 0),
                "stock": str(stock_entry.get() or 0)
            }
            status, body = self.send_api_request("PUT", f"/products/{product_id}", payload)
            if status == 200:
                popup.destroy()
                self.refresh_admin_data() # 수정 성공 시 표 새로고침
            else:
                messagebox.showerror("실패", body)
                
        tk.Button(popup, text="수정 완료", command=on_submit).pack(pady=10)

    # 관리자(Admin) 화면 구성
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
        tk.Button(control_panel, text="새로고침", width=10, command=self.refresh_admin_data).pack(side="left", padx=5)
        tk.Button(control_panel, text="상품 추가", width=10, command=self.show_add_popup).pack(side="left", padx=5)
        tk.Button(control_panel, text="선택 수정", width=10, command=self.show_edit_popup).pack(side="left", padx=5)
        tk.Button(control_panel, text="선택 삭제", width=10, bg="#f44336", fg="white", command=self.delete_product).pack(side="left", padx=5)
        
        # 표 (Treeview) 생성
        columns = ("id", "name", "price", "stock")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="상품명")
        self.tree.heading("price", text="가격(원)")
        self.tree.heading("stock", text="재고(개)")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("stock", width=100, anchor="e")
        self.tree.pack(fill="both", expand=True)

    
    # 직원(Staff) 화면 구성
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