import requests
import json
import pyodbc
import ast
import pandas as pd
import xml.etree.ElementTree as et
import serv_pb2
import serv_pb2_grpc
import grpc
import time
from concurrent import futures
from configparser import ConfigParser
import datetime

status = "yes"
#for i in range(len(data[1]['history'][1])):
#    print((data[1]['history'][1][i]['TRADEDATE']),(data[1]['history'][1][i]['CLOSE']),(data[1]['history'][1][i]['HIGH']),(data[1]['history'][1][i]['LOW']))
class Sender_stock_infServicer(serv_pb2_grpc.Sender_stock_infServicer):

    def chek(self, chek_msg, context):
        response = serv_pb2.chek_stat(stat=status)
        return response
    def takecurdate(self):
        lastBusDay = datetime.datetime.today()
        if datetime.date.weekday(lastBusDay) == 5:  # if it Saturday
            lastBusDay = lastBusDay - datetime.timedelta(days=1)  # then make it Frida
        elif datetime.date.weekday(lastBusDay) == 6:  # if it Sunday
            lastBusDay = lastBusDay - datetime.timedelta(days=2);  # then make it Friday
        return str(lastBusDay).split(" ")[0].replace("-", "")
    def Send_stock_quotes(self,stock_quotes_inp, context):

        #connect
        server_name = configur.get('database', 'server_name')
        database_name = configur.get('database', 'database_name')

        connection_string = 'DRIVER={SQL Server};SERVER=' + server_name + ';DATABASE=' + database_name
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        #connect
        status="no"
        inp_date=stock_quotes_inp.date
        enddate=stock_quotes_inp.enddate
        tiker=stock_quotes_inp.tiker
        curdate= self.takecurdate()
        cursor.execute("select max(datereport) from moex where tiker = '"+tiker+"' and datereport = '"+curdate+"'")
        #print(len(cursor))
        dataintable=2
        for r in cursor:
            print(r[0])
            if (str(r[0]) == "None"):
                dataintable-=1
        cursor.execute("select max(datereport) from moex where tiker = '" + tiker + "' and datereport <= '"+str(inp_date).replace("-", "")+"'")
        for r in cursor:
            print(r[0])
            if (str(r[0]) == "None"):
                dataintable -= 1
        min=""
        max=""
        date = []
        close = []
        high = []
        low = []
        #print(date,tiker)
        if (dataintable!=2):
            #СЧИТЫВАЕМ НЕ ИЗ БД
            response = requests.get("http://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/" + tiker + ".json?iss.json=extended&from=" + inp_date)
            data = ast.literal_eval(response.text)
            cursor.execute("delete from moex where tiker = '" + tiker + "' and datereport>='" + inp_date.replace("-", "") + "'")
            #print(data)
            for i in range(len(data[1]['history'][1])):
                date.append(data[1]['history'][1][i]['TRADEDATE'])
                close.append(data[1]['history'][1][i]['CLOSE'])
                high.append(data[1]['history'][1][i]['HIGH'])
                low.append(data[1]['history'][1][i]['LOW'])

                cursor.execute("insert into moex(tiker,datereport,close_p,low_p,high_p) values('"+str(tiker)+"','"+data[1]['history'][1][i]['TRADEDATE'].replace("-", "")+"',"+str(data[1]['history'][1][i]['CLOSE'])+","+str(data[1]['history'][1][i]['LOW'])+","+str(data[1]['history'][1][i]['HIGH'])+")")
                print(low)
        else:
            #СЧИТЫВАЕМ ИЗ БД
            print("СЧИТЫВАЕМ ИЗ БД")
            cursor.execute("select * from moex where tiker = '" + tiker + "' and datereport>='"+inp_date.replace("-", "")+"'")
            for var in cursor:
                print(var)
                print(var[1])
                print(var[2])
                print(var[3])
                print(var[4])
                date.append(str(var[1]).split(" ")[0])
                close.append(float(var[2]))
                low.append(float(var[3]))
                high.append(float(var[4]))
        #print((data[1]['history'][1][1].keys()))
        response = serv_pb2.stock_quotes_rez(date=date, close=close, high=high, low=low)
        status = "yes"
        connection.commit()
        connection.close()
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
