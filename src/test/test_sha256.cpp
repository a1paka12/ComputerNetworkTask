#include <iostream>
#include <cassert>
#include "../server/include/sha256.hpp"
int main() {
    // 테스트 케이스: "1234"를 해싱했을 때 우리가 예상하는 값과 일치하는가?
    std::string input = "1234";
    std::string expected = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4";
    std::string result = hash_sha256(input);

    std::cout << "입력: " << input << std::endl;
    std::cout << "결과: " << result << std::endl;

    if (result == expected) {
        std::cout << "ok" << std::endl;
    } else {
        std::cout << "false" << std::endl;
        return 1; // 실패 시 에러 코드 반환
    }
    
    return 0;
}