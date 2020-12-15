import serv_pb2
import serv_pb2_grpc
import grpc
from concurrent import futures
from configparser import ConfigParser

configur = ConfigParser()
configur.read('cl_config.ini')
ip = configur.get('network', 'ip')
port_str_min = configur.get('network', 'port_str_min')
port_str_max = configur.get('network', 'port_str_max')
flag=True
port=port_str_min
while flag:
    try:
        print(port)
        channel = grpc.insecure_channel(str(ip) + ':' + str(port))
        stub = serv_pb2_grpc.Sender_stock_infStub(channel)
        reaqest = serv_pb2.chek_msg(msg="1")
        response = stub.chek(reaqest)
        flag=False
    except:
        if port>port_str_max:
            port=port_str_min
        else:
            port+=1
print('Connect ' + str(ip) + ':' + str(port))
print("Введите тикер, Exit-выход")
tiker=input()
while (tiker!="Exit"):
    try:
        print("Введите дату начала промежутка")
        date=input()
        enddate=""
        #date="2020-12-10"
        #tiker="SBER"
        reaqest = serv_pb2.stock_quotes_inp(date=date, enddate=enddate, tiker=tiker)
        response = stub.Send_stock_quotes(reaqest)
        for i in range(len(response.date)):
            print(response.date[i],response.low[i])
        print("Введите тикер, Exit-выход")
        tiker = input()
    except:
        flag = True
        port = port_str_min
        while flag:
            try:
                print(port)
                channel = grpc.insecure_channel(str(ip) + ':' + str(port))
                stub = serv_pb2_grpc.Sender_stock_infStub(channel)
                reaqest = serv_pb2.chek_msg(msg="1")
                response = stub.chek(reaqest)
                flag = False
            except:
                if port > port_str_max:
                    port = port_str_min
                else:
                    port += 1
        print('Connect ' + str(ip) + ':' + str(port))
        print("Введите тикер, Exit-выход")
        tiker = input()


