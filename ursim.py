import socket
import time

def main():
    HOST = "192.168.0.31"  # UR 로봇 혹은 URSim의 IP 주소
    PORT = 30002  # 대체적으로 사용되는 포트 번호

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    # URScript를 정의
    URScript = "movej([1.57, -1.57, -1.57, -1.57, 1.57, 0], a=1.2, v=0.3)\n"

    # URScript 전송
    s.send(URScript.encode())

    data = s.recv(1024)
    s.close()
    print("Received", repr(data))

if __name__ == '__main__':
    main()
