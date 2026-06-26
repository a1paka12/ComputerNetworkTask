#include "httpResponse.hpp"
#include <sstream>

HttpResponse::HttpResponse() 
    : status_code(200), status_message("OK"), content_type("application/json; charset=utf-8") {}

void HttpResponse::setStatus(int code, const std::string& message) {
    status_code = code;
    status_message = message;
}

std::string HttpResponse::toString() const {
    std::ostringstream response;
    response << "HTTP/1.1 " << status_code << " " << status_message << "\r\n"
             << "Content-Type: " << content_type << "\r\n"
             << "Content-Length: " << body.length() << "\r\n"
             << "Connection: close\r\n"
             << "\r\n"
             << body;
    return response.str();
}