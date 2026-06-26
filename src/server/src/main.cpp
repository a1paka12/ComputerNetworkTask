#include <iostream>
#include <string>

#include "httpServer.hpp"
#include "login.hpp"
#include "DBSearch.hpp"

using namespace std;

// API 로직 처리기

// 로그인 처리 함수
void handleLogin(const HttpRequest& req, HttpResponse& res) {
    string user_id = req.extractJsonValue("id");
    string user_pw = req.extractJsonValue("pw");
    
    LoginResult auth_result = Login::authenticate(user_id, user_pw);
    
    string status_msg = (auth_result.status_code == 200) ? "OK" : 
                       (auth_result.status_code == 401) ? "Unauthorized" : "Internal Server Error";
    
    res.setStatus(auth_result.status_code, status_msg);
    
    if (auth_result.status_code == 200) {
        res.body = "{\"status\": \"success\", \"role\": \"" + auth_result.role + "\"}";
    } else {
        res.body = "{\"status\": \"fail\", \"error\": \"" + auth_result.message + "\"}";
    }
}

//로그아웃 함수
void handleLogout(const HttpRequest& req, HttpResponse& res) {
    string id = req.extractJsonValue("id"); // 클라이언트가 보낸 ID
    Login::logout(id); // 아까 만든 logout 함수 호출
    res.setStatus(200, "OK");
    res.body = "{\"message\": \"Logout Successful\"}";
}

// 상품 조회 처리 함수
void handleProductSearch(const HttpRequest& req, HttpResponse& res) {
    try {
        // "/products/123" 에서 ID(123)만 추출
        int product_id = stoi(req.uri.substr(10));
        string product_json = DBSearch::getProductById(product_id);
        
        if (!product_json.empty()) {
            res.setStatus(200, "OK");
            res.body = product_json;
        } else {
            res.setStatus(404, "Not Found");
            res.body = "{\"error\": \"Product not found\"}";
        }
    } catch (...) {
        res.setStatus(400, "Bad Request");
        res.body = "{\"error\": \"Invalid product ID format\"}";
    }
}

//전체 상품 조회 (Admin & Staff 공통)
void handleGetAllProducts(const HttpRequest& req, HttpResponse& res) {
    string json_list = DBSearch::getAllProducts();
    res.setStatus(200, "OK");
    res.body = json_list;
}

//상품 정보 수정 (Admin 전용)
void handleUpdateProduct(const HttpRequest& req, HttpResponse& res) {
    try {
        // URL에서 ID 추출
        size_t last_slash = req.uri.find_last_of('/');
        string id_str = req.uri.substr(last_slash + 1);
        if (id_str.empty()) throw invalid_argument("Empty ID");
        int product_id = stoi(id_str);
        
        // JSON 파싱
        string name = req.extractJsonValue("name");
        string price_str = req.extractJsonValue("price");
        string stock_str = req.extractJsonValue("stock");

        if (name.empty() || price_str.empty() || stock_str.empty()) {
            res.setStatus(400, "Bad Request");
            res.body = "{\"error\": \"데이터가 누락되었거나 JSON 형식이 잘못되었습니다 (따옴표 필요)\"}";
            return;
        }

        // 숫자로 변환
        int price = stoi(price_str);
        int stock = stoi(stock_str);

        // DB 업데이트 실행
        if (DBSearch::updateProduct(product_id, name, price, stock)) {
            res.setStatus(200, "OK");
            res.body = "{\"status\":\"success\", \"message\":\"업데이트 완료\"}";
        } else {
            res.setStatus(500, "Server Error");
        }
    } 
    catch (const exception& e) {
        res.setStatus(400, "Bad Request");
        res.body = "{\"error\": \"숫자 변환 실패 또는 잘못된 요청입니다.\"}";
    }
}

//상품 추가
void handleAddProduct(const HttpRequest& req, HttpResponse& res) {
    string name = req.extractJsonValue("name");
    string category = req.extractJsonValue("category");
    
    // 만약 빈 값이 넘어오면 에러 처리
    if (name.empty() || req.extractJsonValue("price").empty()) {
        res.setStatus(400, "Bad Request");
        res.body = "{\"error\": \"Missing product data\"}";
        return;
    }
    
    int price = stoi(req.extractJsonValue("price"));
    int stock = stoi(req.extractJsonValue("stock"));

    if (DBSearch::addProduct(name, category, price, stock)) {
        res.setStatus(201, "Created");
        res.body = "{\"status\":\"success\", \"message\":\"상품이 추가되었습니다.\"}";
    } else {
        res.setStatus(500, "Server Error");
    }
}

//상품 삭제 처리 함수 (DELETE /products/{id})
void handleDeleteProduct(const HttpRequest& req, HttpResponse& res) {
    try {
        size_t last_slash = req.uri.find_last_of('/');
        int product_id = stoi(req.uri.substr(last_slash + 1));

        if (DBSearch::deleteProduct(product_id)) {
            res.setStatus(200, "OK");
            res.body = "{\"status\":\"success\", \"message\":\"상품이 삭제되었습니다.\"}";
        } else {
            res.setStatus(404, "Not Found");
            res.body = "{\"error\": \"존재하지 않는 상품 ID입니다.\"}";
        }
    } catch (...) {
        res.setStatus(400, "Bad Request");
        res.body = "{\"error\": \"잘못된 ID 형식입니다.\"}";
    }
}

// 메인 서버 구동부
int main() {
    HttpServer server(80);

    // 로그인/로그아웃 라우팅 등록
    server.post("/login", handleLogin);
    server.post("/logout", handleLogout);
    // CRUD 라우팅 등록
    server.get("/products", handleGetAllProducts);         // READ (전체)
    server.get("/products/*", handleProductSearch);        // READ (단일)
    server.post("/products", handleAddProduct);            // CREATE
    server.put("/products/*", handleUpdateProduct);        // UPDATE
    server.Delete("/products/*", handleDeleteProduct);     // DELETE

    // 서버 시작
    server.start();

    return 0;
}