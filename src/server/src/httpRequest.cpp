#include "httpRequest.hpp"
#include <sstream>

bool HttpRequest::parse(const std::string& raw_request) {
    if (raw_request.empty()) return false;

    // 헤더와 바디 분리 (\r\n\r\n 기준)
    size_t body_pos = raw_request.find("\r\n\r\n");
    std::string headers_part;
    
    if (body_pos != std::string::npos) {
        headers_part = raw_request.substr(0, body_pos);
        body = raw_request.substr(body_pos + 4);
    } else {
        headers_part = raw_request;
        body = "";
    }

    // 첫 줄(Request Line) 파싱
    std::istringstream stream(headers_part);
    std::string first_line;
    std::getline(stream, first_line);

    std::istringstream line_stream(first_line);
    line_stream >> method >> uri >> version;

    return !method.empty() && !uri.empty();
}

std::string HttpRequest::extractJsonValue(const std::string& key) const {
    // 간단히 {"id":"admin"} 형태에서 값을 뽑음.
    std::string search_key = "\"" + key + "\":";
    size_t key_pos = body.find(search_key);
    
    if (key_pos == std::string::npos) {
        // 띄어쓰기가 있는 경우도 고려 {"id": "admin"}
        search_key = "\"" + key + "\": ";
        key_pos = body.find(search_key);
        if (key_pos == std::string::npos) return "";
    }

    size_t start_quote = body.find("\"", key_pos + search_key.length());
    if (start_quote == std::string::npos) return "";

    size_t end_quote = body.find("\"", start_quote + 1);
    if (end_quote == std::string::npos) return "";

    return body.substr(start_quote + 1, end_quote - start_quote - 1);
}