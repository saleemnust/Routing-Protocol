import threading
import time
import sys
from datetime import datetime
from socket import *
import json
from collections import OrderedDict
import collections
import operator



def Bellmanford(received_update):
        global update_vector
        for i in received_update:
                for j in received_update[i]:
                        if j in update_vector.keys():
                                if  (update_vector[j][0] > received_update[i][j][0] + update_vector[i][0]):
                                        update_vector[j][0]=received_update[i][j][0] + update_vector[i][0]
                                        update_vector[j][1]=update_vector[i][1]+received_update[i][j][1]
                                #update_vector[j][0]= min (update_vector[j][0], received_update[i][j][0] + update_vector[i][0])
                                #if (update_vector[j][0]==received_update[i][j][0] + update_vector[i][0]):
                                        
                        else:
                                if (j==router_name):
                                                update_vector[j]=[0,router_name+router_name]
                                else:
                                                update_vector[j]=[received_update[i][j][0]+update_vector[i][0], update_vector[i][1]+received_update[i][j][1]]
def clientSide(serverPort):
	global serverIP,router_name,update_vector
	clientSocket = socket(AF_INET, SOCK_DGRAM)
	while (True):
                message = json.dumps(update_vector)
                list = [router_name,message]
                #message = ast.literal_eval(json.dumps(list))
                message = json.dumps(list)
                clientSocket.sendto(message,(serverIP, serverPort))
                modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
                if (modifiedMessage=="Received"):
                        clientSocket.close() # Close the socket
                        break
                

def active_host(port): 
	global serverIP
	status = -1
	flagsocket = socket(AF_INET, SOCK_DGRAM)
	try:
		data = "hello"
		flagsocket.sendto(data,(serverIP,port))
		message,serverAddress=flagsocket.recvfrom(2048)
		status=1
	except:
		status=0
	flagsocket.close()
	return status
	
def client_status():
        global flag
	while (True):
		global myneighbors
		for key,val in myneighbors.items():
			response = active_host(int(val[0]))
			if (response == 1):
				clientSide(val[0])
		time.sleep( 3 )
		
def router_status():
        global update_vector
        sorted_update_vector = (sorted(update_vector.items(), key=lambda t: t[0]))
	print "I am Router", router_name
	length=len(sorted_update_vector)
	newpath=""
	for i in range(length):
                if (sorted_update_vector[i][0]!=router_name):
                        path = sorted_update_vector[i][1][1]
                        for x in range(len(path)-1):
                                if (path[x]!=path[x+1]):
                                        newpath=newpath+path[x]
                        newpath=newpath+path[-1]
                        print "Least cost path to router",sorted_update_vector[i][0],":",newpath,"and the cost:",sorted_update_vector[i][1][0]
                        newpath=""
                        path=""
						
def serverSide(serverPort):
	global serverIP,flag
	serverSocket = socket(AF_INET, SOCK_DGRAM)
	serverSocket.bind((serverIP,serverPort))
	dist_vector={}
	global rcv_update
	while 1:
                message, clientAddress = serverSocket.recvfrom(2048)
                if (message=="hello"):
                        modified_message = "Received"
                        serverSocket.sendto(modified_message, clientAddress)        
		else:
			list = json.loads(message)
			modified_message = "Received"
			serverSocket.sendto(modified_message, clientAddress)
			neighbor=list[0]
			#print  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			dst_vector = json.loads(list[1])
			dist_vector.clear()
                        for key,val in dst_vector.items():
                                key=key.encode('ascii','ignore')
                                val[1]=val[1].encode('ascii','ignore')
                                dist_vector[key]=[val[0],val[1]]
                        neighbor = neighbor.encode('ascii','ignore')
                        if neighbor not in rcv_update.keys():
                                rcv_update[neighbor] = dist_vector.copy()
                                Bellmanford(rcv_update)
                                flag = 0
                        elif (dist_vector!=rcv_update[neighbor]):
                                rcv_update[neighbor] = dist_vector.copy()
                                Bellmanford(rcv_update)
                                flag = 0
                        else:
                                flag = flag + 1
                                if (flag==5):
                                        router_status()
def main():
        time.sleep(15)
	global serverIP,myneighbors,router_name,update_vector,rcv_update,flag
	flag=0
	serverIP="127.0.0.1"
	myneighbors = {}
	update_vector={}
	rcv_update={}
	router_name=sys.argv[1]
	global myport
	port=sys.argv[2]
	myport=int(port)
	f = open(sys.argv[3], 'r')
	lines = f.read() 
	splitLine = (lines.split())
	a = splitLine[0]
	i=1
	while(i!=len(splitLine)):
		 update_vector[splitLine[i]] = [float(splitLine[i+1]),(router_name+splitLine[i])]
		 myneighbors[splitLine[i]]=[int(splitLine[i+2])]
		 i=i+3
	thread = threading.Thread(target=client_status)
	thread.start()
        thread1 = threading.Thread( target=serverSide(int(port)) )
	thread1.start()
if __name__ == "__main__":
       main()

