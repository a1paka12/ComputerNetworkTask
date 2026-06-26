#include "DBSearch.hpp"
#include <sqlite3.h>
#include <sstream>

std::string DBSearch::getProductById(int product_id) {
    sqlite3* db;
    if (sqlite3_open("ecommerce.db", &db) != SQLITE_OK) return "";

    std::string result = "";
    const char* sql = "SELECT name, category, price, stock FROM products WHERE id = ?";
    sqlite3_stmt* stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, product_id);
        
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            std::string name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
            std::string category = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
            int price = sqlite3_column_int(stmt, 2);
            int stock = sqlite3_column_int(stmt, 3);

            // JSON 문자열 조립
            std::ostringstream json;
            json << "{\n"
                 << "  \"id\": " << product_id << ",\n"
                 << "  \"name\": \"" << name << "\",\n"
                 << "  \"category\": \"" << category << "\",\n"
                 << "  \"price\": " << price << ",\n"
                 << "  \"stock\": " << stock << "\n"
                 << "}";
            result = json.str();
        }
        sqlite3_finalize(stmt);
    }
    sqlite3_close(db);
    return result;
}

std::string DBSearch::getAllProducts() {
    sqlite3* db;
    if (sqlite3_open("db/ecommerce.db", &db) != SQLITE_OK) return "[]";

    std::string result = "[";
    const char* sql = "SELECT id, name, category, price, stock FROM products";
    sqlite3_stmt* stmt;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        bool first = true;
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            if (!first) result += ",";
            result += "{";
            result += "\"id\":" + std::to_string(sqlite3_column_int(stmt, 0)) + ",";
            result += "\"name\":\"" + std::string(reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1))) + "\",";
            result += "\"price\":" + std::to_string(sqlite3_column_int(stmt, 3)) + ",";
            result += "\"stock\":" + std::to_string(sqlite3_column_int(stmt, 4));
            result += "}";
            first = false;
        }
        sqlite3_finalize(stmt);
    }
    sqlite3_close(db);
    result += "]";
    return result;
}

bool DBSearch::updateProduct(int id, const std::string& name, int price, int stock) {
    sqlite3* db;
    if (sqlite3_open("db/ecommerce.db", &db) != SQLITE_OK) return false;

    // 트랜잭션 시작 (BEGIN)
    sqlite3_exec(db, "BEGIN TRANSACTION;", nullptr, nullptr, nullptr);

    const char* sql = "UPDATE products SET name=?, price=?, stock=? WHERE id=?";
    sqlite3_stmt* stmt;
    bool success = false;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, name.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_int(stmt, 2, price);
        sqlite3_bind_int(stmt, 3, stock);
        sqlite3_bind_int(stmt, 4, id);

        if (sqlite3_step(stmt) == SQLITE_DONE) {
            success = true;
        }
        sqlite3_finalize(stmt);
    }

    // 성공하면 적용(COMMIT), 실패하면 원상복구(ROLLBACK)
    if (success) {
        sqlite3_exec(db, "COMMIT;", nullptr, nullptr, nullptr);
    } else {
        sqlite3_exec(db, "ROLLBACK;", nullptr, nullptr, nullptr);
    }
    
    sqlite3_close(db);
    return success;
}

bool DBSearch::addProduct(const std::string& name, const std::string& category, int price, int stock) {
    sqlite3* db;
    if (sqlite3_open("db/ecommerce.db", &db) != SQLITE_OK) return false;

    const char* sql = "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)";
    sqlite3_stmt* stmt;
    bool success = false;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_text(stmt, 1, name.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_text(stmt, 2, category.c_str(), -1, SQLITE_TRANSIENT);
        sqlite3_bind_int(stmt, 3, price);
        sqlite3_bind_int(stmt, 4, stock);

        // INSERT 실행
        if (sqlite3_step(stmt) == SQLITE_DONE) {
            success = true;
        }
        sqlite3_finalize(stmt);
    }
    
    sqlite3_close(db);
    return success;
}

bool DBSearch::deleteProduct(int id) {
    sqlite3* db;
    if (sqlite3_open("db/ecommerce.db", &db) != SQLITE_OK) return false;

    const char* sql = "DELETE FROM products WHERE id = ?";
    sqlite3_stmt* stmt;
    bool success = false;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, nullptr) == SQLITE_OK) {
        sqlite3_bind_int(stmt, 1, id);

        // DELETE 실행
        if (sqlite3_step(stmt) == SQLITE_DONE) {
            // 변경된 행(row)이 1개 이상인지 확인 (없는 ID를 지우려고 하면 false)
            if (sqlite3_changes(db) > 0) {
                success = true;
            }
        }
        sqlite3_finalize(stmt);
    }

    sqlite3_close(db);
    return success;
}