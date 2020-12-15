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
import  subprocess
import sys
import  multiprocessing as mp
from multiprocessing import Process

configur = ConfigParser()
configur.read('serv_config.ini')
ip = configur.get('network', 'ip')
port = configur.get('network', 'port')
try:
    channel = grpc.insecure_channel(str(ip) + ':' + str(port))
    stub = serv_pb2_grpc.Sender_stock_infStub(channel)
    reaqest = serv_pb2.chek_msg(msg="1")
    response = stub.chek(reaqest)
except:
    print("Запускаем сервер")
    p1=subprocess.Popen([sys.executable, "main.py"])
    p1.communicate()


