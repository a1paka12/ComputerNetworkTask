#include "login.hpp"
#include <iostream>
#include "sha256.hpp" 
#include <sqlite3.h>

LoginResult Login::authenticate(const std::string& username, const std::string& password) {
    std::string hashed_pw = hash_sha256(password);
    
    // 기본 상태를 401(실패)로 셋팅
    LoginResult result = {401, "", "Invalid ID or Password"};

    sqlite3* db;
    // DB 연결 실패 시 500 에러 반환
    if (sqlite3_open("ecommerce.db", &db) != SQLITE_OK) {
        return {500, "", "Database Connection Failed"};
    }

    const char* sql = "SELECT role FROM users WHERE username = ? AND password_hash = ?";
    sqlite3_stmt* stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, username.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 2, hashed_pw.c_str(), -1, SQLITE_TRANSIENT);

        // 정보가 일치하면 200(성공)로
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            result.status_code = 200;
            result.role = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            result.message = "Login Successful";
        }
        sqlite3_finalize(stmt);
    }
    sqlite3_close(db);
    
    return result; // 401 또는 200 리턴
}