# encoding: utf-8
import threading
import socket
import time
import presenter_message_pb2 as pb2
import time
from presenter_types import *
import ChannelManager


SEND_BUF_SIZE = 102400
RECV_BUF_SIZE = 102400


class PresenterSocketClient(object):
    def __init__(self, server_address, reconnectiontime=5,recvCallback=None):
        self._server_address = server_address
        self._reconnectiontime = reconnectiontime
        self.__recvCallback = recvCallback
        self._sock_client = None
        self._bstart = True
        # threading.Thread(target=self.start_connect()).start()

    def start_connect(self):
        print("创建socket对象...")
        self._sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock_client.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, SEND_BUF_SIZE)
        self._sock_client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, RECV_BUF_SIZE)
        try:
            print("连接服务器...")
            self._sock_client.connect(self._server_address)
        except Exception as e:
            print(e)
            print("正在重新连接...")
            time.sleep(self._reconnectiontime)
            self.start_connect()
            return
        self._bstart = True
        print("监听数据接受中...")
        threading.Thread(target=self.__start_listenning()).start()

    def __start_listenning(self):
        while self._bstart:
            try:
                # print("等待数据到达...")
                data = self._sock_client.recv(RECV_BUF_SIZE)
                if data:
                    if self.__recvCallback:
                        self.__recvCallback(data)
                    #print(data)
                    # self.send_data("hello".encode())
                else:
                    print("close")
                    self._sock_client.close()
                    self.start_connect()
                    break
            except Exception as e:
                print(e)
                self._sock_client.close()
                self.start_connect()
                break

    def send_data(self, data):
	# print(data)
        self._sock_client.sendall(data)

    def close(self):
        self._bstart = False
        self._sock_client.shutdown()
        self._sock_client.close()


if __name__ == "__main__":
    print('start client...')

    def recvdata(data):
        print(data)

    psc = PresenterSocketClient(("192.168.1.246", 7006), 5, recvdata)
    threading.Thread(target=psc.start_connect).start()
    channel_manager = ChannelManager.ChannelManager()
    data = channel_manager.OpenChannel()


    image_data = b''
    with open('test.jpg', mode='rb') as f:
        image_data = f.read()

    image_frame = ImageFrame()
    image_frame.format = 0
    image_frame.width = 300
    image_frame.height = 200
    image_frame.data = image_data
    image_frame.size = 0
    image_frame.detection_results = DetectionResult()
    image_frame.detection_results.lt.x = 10
    image_frame.detection_results.lt.y = 10
    image_frame.detection_results.rb.x = 100
    image_frame.detection_results.rb.y = 100
    image_frame.detection_results.result_text = 'fuck you!'
    all_data = channel_manager.PackRequestData(image_frame)
    while True:
        raw_input('please input data you need to send:')
        psc.send_data(data)
        index = 0
        while index < 20:
            psc.send_data(all_data)
            time.sleep(0.2)
            index = index + 1
    # print('client is running...')
    # while True:
    #     raw_input('please input data you need to send:')
    #     # psc.send_data(str.encode(data))
    #     # 打开通道，建立连接
    #     message = pb2.OpenChannelRequest()
    #     message.channel_name = 'video'
    #     message.content_type = 1
    #     msg_data = message.SerializeToString()
    #     msg_data_len = len(msg_data)
    #     msg_name = pb2._OPENCHANNELREQUEST.full_name
    #     print('msg_name:', msg_name)
    #     msg_name_len = len(msg_name)
    #     print('msg_name_len:', msg_name_len)
    #     msg_total_len = msg_name_len+5+msg_data_len
    #     print('msg_total_len:', msg_total_len)
    #     data = b''
    #     msg_total_len = socket.htonl(msg_total_len)
    #     print('socket.htonl(msg_total_len)=', msg_total_len)
    #     pack_data = struct.pack('IB', msg_total_len, msg_name_len)
    #     print('pack_data length=', len(pack_data))
    #     data += pack_data
    #     data += msg_name.encode()
    #     data += msg_data
    #
    #     psc.send_data(data)
    #     time.sleep(1)
    #
    #     #发送数据
    #
    #     image_data = b''
    #     image_len = 0
    #     with open('test.jpg', mode='rb') as f:
    #         image_data = f.read()
    #         image_len = len(image_data)
    #
    #     msg_name = pb2._PRESENTIMAGEREQUEST.full_name
    #     print('msg_name:', msg_name)
    #     msg_name_len = len(msg_name)
    #     print('msg_name_len:', msg_name_len)
    #
    #     request = pb2.PresentImageRequest()
    #     request.format = 0
    #     request.width = 300
    #     request.height = 200
    #     request.data = image_data
    #     myadd = request.rectangle_list.add()
    #     myadd.left_top.x = 1
    #     myadd.left_top.x = 2
    #     myadd.right_bottom.x = 3
    #     myadd.right_bottom.y = 4
    #     myadd.label_text = 'hello'
    #     buf = request.SerializeToString()
    #
    #     msg_body_len = len(buf)
    #     msg_total_len = msg_name_len+5 + msg_body_len
    #     print('msg_total_len:', msg_total_len)
    #     data = b''
    #     msg_total_len = socket.htonl(msg_total_len)
    #     print('socket.htonl(msg_total_len)=', msg_total_len)
    #     pack_data = struct.pack('IB', msg_total_len, msg_name_len)
    #     print('pack_data length=', len(pack_data))
    #     data += pack_data
    #     data += msg_name.encode()
    #     data += buf
    #
    #     index = 0
    #     while index < 20:
    #         psc.send_data(data)
    #         time.sleep(0.2)
    #         index = index + 1

        # msg_head = data[0:5]
        # print('msg_head data is', msg_head)
        # print('msg_head_len:', len(msg_head))
        # msg_head_data = struct.Struct('IB')
        # (msg_total_len, msg_name_len) = msg_head_data.unpack(msg_head)
        # msg_total_len = socket.ntohl(msg_total_len)
        # print('pack msg_total_len:', msg_total_len)
        # print('pack msg_n ame_len:', msg_name_len)
        # psc.send_data(data)
