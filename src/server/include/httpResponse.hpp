#ifndef HTTP_RESPONSE_HPP
#define HTTP_RESPONSE_HPP

#include <string>

class HttpResponse {
public:
    int status_code;
    std::string status_message;
    std::string content_type;
    std::string body;

    // 기본 생성자 (기본값: 200 OK, JSON 포맷)
    HttpResponse();

    // 상태 코드와 메시지를 변경하는 헬퍼 함수
    void setStatus(int code, const std::string& message);
    
    // 최종적으로 소켓에 보낼 수 있는 문자열로 변환
    std::string toString() const;
};

#endif