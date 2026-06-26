#include "httpServer.hpp"
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>

using namespace std;

HttpServer::HttpServer(int port) : port(port), server_fd(-1) {}

HttpServer::~HttpServer() {
    if (server_fd >= 0) close(server_fd);
}

// API 등록 함수들
void HttpServer::get(const string& path, HandlerFunc handler) {
    routes.push_back({"GET", path, handler});
}

void HttpServer::post(const string& path, HandlerFunc handler) {
    routes.push_back({"POST", path, handler});
}

void HttpServer::put(const std::string& path, HandlerFunc handler){
    routes.push_back({"PUT", path, handler});
}

void HttpServer::Delete(const std:: string& path, HandlerFunc handler){
    routes.push_back({"DELETE", path, handler});
}

void HttpServer::head(const std:: string& path, HandlerFunc handler){
    routes.push_back({"HEAD", path, handler});
}

// URI 매칭 로직 (/products/* 처럼 끝에 *가 붙으면 접두사 매칭 지원)
bool HttpServer::matchRoute(const string& req_uri, const string& route_path) {
    if (!route_path.empty() && route_path.back() == '*') {
        string prefix = route_path.substr(0, route_path.length() - 1);
        return req_uri.find(prefix) == 0;
    }
    return req_uri == route_path;
}

bool HttpServer::initSocket() {
    int opt = 1;
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) return false;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in address;
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY; 
    address.sin_port = htons(port);

    if (::bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) return false;
    if (::listen(server_fd, 10) < 0) return false;
    return true;
}

void HttpServer::start() {
    if (!initSocket()) {
        cerr << "[Error] 서버 소켓 초기화 실패" << endl;
        return;
    }

    cout << "서버가 " << port << " 포트에서 실행 중...\n" << endl;

    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[4096] = {0};

    // 무한 루프 시작
    while (true) {
        int client_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen);
        if (client_socket < 0) continue;

        memset(buffer, 0, sizeof(buffer));
        read(client_socket, buffer, sizeof(buffer) - 1);
        
        HttpRequest req;
        HttpResponse res;
        
        if (req.parse(buffer)) {
            cout << "[" << req.method << "] " << req.uri << " 요청 수신" << endl;

            bool routed = false;
            // 등록된 라우팅 찾기
            for (const auto& route : routes) {
                if (req.method == route.method && matchRoute(req.uri, route.path)) {
                    // 매칭되는 경로를 찾으면 해당 콜백 함수를 실행
                    route.handler(req, res);
                    routed = true;
                    break;
                }
            }

            // 일치하는 API가 없으면 404 에러 반환
            if (!routed) {
                res.setStatus(404, "Not Found");
                res.body = "{\"error\": \"Route not found\"}";
            }
        } else {
            res.setStatus(400, "Bad Request");
        }

        // 응답 전송 및 소켓 닫기
        string response_str = res.toString();
        send(client_socket, response_str.c_str(), response_str.length(), 0);
        close(client_socket);
    }
}