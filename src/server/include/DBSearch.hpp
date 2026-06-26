#ifndef DBSEARCH_HPP
#define DBSEARCH_HPP
#include <string>

class DBSearch {
public:
    static std::string getProductById(int product_id);
    
    // Admin용 전체 조회 (GET)
    static std::string getAllProducts();
    
    // Admin용 상품 추가 (POST)
    static bool addProduct(const std::string& name, const std::string& category, int price, int stock);
    
    // Admin용 상품 수정 (PUT) - 트랜잭션 적용
    static bool updateProduct(int id, const std::string& name, int price, int stock);
    
    // Admin용 상품 삭제 (DELETE)
    static bool deleteProduct(int id);
};

#endif