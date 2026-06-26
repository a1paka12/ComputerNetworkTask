#ifndef HTTPSERVER_HPP
#define HTTPSERVER_HPP

#include <string>
#include <vector>
#include <functional>
#include "httpRequest.hpp"
#include "httpResponse.hpp"

// 라우팅할 함수(콜백)의 형태를 정의
using HandlerFunc = std::function<void(const HttpRequest& req, HttpResponse& res)>;

// 라우팅 정보
struct Route {
    std::string method;
    std::string path;
    HandlerFunc handler;
};

class HttpServer {
private:
    int port;
    int server_fd;
    std::vector<Route> routes;

    // 내부 소켓 설정 함수
    bool initSocket();
    // 경로 매칭 확인 함수 (와일드카드 '*' 지원 - 예: /products/*)
    bool matchRoute(const std::string& req_uri, const std::string& route_path);

public:
    HttpServer(int port);
    ~HttpServer();

    // 라우터 등록 함수
    void get(const std::string& path, HandlerFunc handler);
    void post(const std::string& path, HandlerFunc handler);
    void put(const std::string& path, HandlerFunc handler);
    void Delete(const std:: string& path, HandlerFunc handler);
    void head(const std:: string& path, HandlerFunc handler);

    // 서버 시작 루프 (소켓 연결 및 라우팅 자동 처리)
    void start();
};

#endif