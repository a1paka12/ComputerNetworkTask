#ifndef HTTP_REQUEST_HPP
#define HTTP_REQUEST_HPP

#include <string>

class HttpRequest {
public:
    std::string method;  // GET, POST, PUT 등
    std::string uri;     // /login, /products/1 등
    std::string version; // HTTP/1.1
    std::string body;    // JSON 데이터 (예: {"id":"admin", "pw":"1234"})

    // 소켓에서 읽은 raw 문자열을 파싱
    bool parse(const std::string& raw_request);
    
    // Body(JSON)에서 특정 키의 값을 추출하는 함수
    std::string extractJsonValue(const std::string& key) const;
};

#endif