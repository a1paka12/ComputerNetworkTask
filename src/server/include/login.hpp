#ifndef LOGIN_HPP
#define LOGIN_HPP
#include <string>

// 로그인 결과를 명확하게 담을 구조체
struct LoginResult {
    int status_code;       // 200(성공), 401(실패), 500(서버 에러) 등
    std::string role;      // admin 또는 staff (실패 시 빈 문자열)
    std::string message;   // 에러 메시지 또는 성공 메시지
};

class Login {
public:
    static LoginResult authenticate(const std::string& username, const std::string& password);
};

#endif