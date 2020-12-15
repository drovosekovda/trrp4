import requests
import json
import ast
import pandas as pd
import xml.etree.ElementTree as et
import serv_pb2
import serv_pb2_grpc
import grpc
import time
from concurrent import futures
from configparser import ConfigParser

status = "yes"
#for i in range(len(data[1]['history'][1])):
#    print((data[1]['history'][1][i]['TRADEDATE']),(data[1]['history'][1][i]['CLOSE']),(data[1]['history'][1][i]['HIGH']),(data[1]['history'][1][i]['LOW']))
class Sender_stock_infServicer(serv_pb2_grpc.Sender_stock_infServicer):

    def chek(self, chek_msg, context):
        response = serv_pb2.chek_stat(stat=status)
        return response
    def Send_stock_quotes(self,stock_quotes_inp, context):
        status="no"
        date=stock_quotes_inp.date
        enddate=stock_quotes_inp.enddate
        tiker=stock_quotes_inp.tiker
        #print(date,tiker)
        response = requests.get("http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/" + tiker + ".json?iss.json=extended&from=" + date)
        data = ast.literal_eval(response.text)
        date=[]
        close=[]
        high=[]
        low=[]
        #print(data)
        for i in range(len(data[1]['history'][1])):
            date.append(data[1]['history'][1][i]['TRADEDATE'])
            close.append(data[1]['history'][1][i]['CLOSE'])
            high.append(data[1]['history'][1][i]['HIGH'])
            low.append(data[1]['history'][1][i]['LOW'])
        print(low)
        #print((data[1]['history'][1][1].keys()))
        response = serv_pb2.stock_quotes_rez(date=date, close=close, high=high, low=low)
        status = "yes"
        return response
configur = ConfigParser()
configur.read('serv_config.ini')
ip = configur.get('network', 'ip')
port = configur.get('network', 'port')
server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
serv_pb2_grpc.add_Sender_stock_infServicer_to_server(Sender_stock_infServicer(), server)
print('Starting server on ' + str(ip) + ':' + str(port))
server.add_insecure_port( str(ip) + ':' + str(port) )
server.start()
server.wait_for_termination()
#python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. serv.proto
