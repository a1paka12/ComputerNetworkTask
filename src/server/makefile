# 컴파일러 및 옵션 설정
CXX = g++
OPENSSL_PATH = $(shell brew --prefix openssl)
CXXFLAGS = -Wall -std=c++17 -Iinclude -I$(OPENSSL_PATH)/include
LDFLAGS = -lsqlite3 -L$(OPENSSL_PATH)/lib -lssl -lcrypto

# 디렉토리 구조 설정
SRC_DIR = src
INC_DIR = include
OBJ_DIR = obj
BIN_DIR = bin

# 최종 실행 파일 이름
TARGET = $(BIN_DIR)/server

# 소스 파일(.cpp)과 오브젝트 파일(.o) 자동 매핑
SRCS = $(wildcard $(SRC_DIR)/*.cpp)
OBJS = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRCS))

# 기본 빌드 타겟
all: prepare $(TARGET)

# 폴더가 없으면 자동으로 생성 (빌드 에러 방지)
prepare:
	@mkdir -p $(OBJ_DIR)
	@mkdir -p $(BIN_DIR)

# 최종 실행 파일 링킹 (Linking)
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDFLAGS)
	@echo "빌드 성공, 위치: $(TARGET)"

# 개별 .cpp 파일을 .o 파일로 컴파일
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# 빌드 산출물 삭제 (초기화)
clean:
	rm -rf $(OBJ_DIR)/*.o $(TARGET)
	@echo "빌드 파일 정리"

# 빌드 후 바로 실행하는 단축 명령어
run: all
	@echo "서버를 시작..."
	@./$(TARGET)