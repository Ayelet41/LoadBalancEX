from japronto import Application
import requests
from time import sleep
import threading
import backoff
import logging


logging.basicConfig(filename='appj.log',level=logging.ERROR)

class loadB(object):
    servers=[] #assume only one identifer
    stats_post={}
    stats_get={}
    lastRR=0
    lock = threading.Lock()
    #MAXRETRY=10

    def __init__(self,serverList):
        logging.info("Started Load Balancer config for:"+str(serverList))
        self.servers=serverList
        #start_stats:
        for server in servers:
            self.stats_get[server]=0
            self.stats_post[server]=0
        logging.debug(self.stats_get,self.stats_post)

    def getRR(self):#get the current server number
        return self.lastRR

    def addRR(self):# increase the current number
        self.lock.acquire()
        if self.lastRR ==len(self.servers)-1:
            self.lastRR=0
        else:
            self.lastRR +=1
        self.lock.release()


    #for statistics as there are several sources not good for long trem solution
    def addget(self,server):
        self.stats_get[server]+=1
        logging.info("StatsGet"+str(self.stats_get))

    def addpost(self,server):
        self.stats_post[server]+=1
        logging.info("StatsPost"+str(self.stats_post))
    def len(self):
        return len(self.servers)
    def getSer(self,i):
        if self.servers[i]:
            return self.servers[i]



###Application routes



def backoff_hdlr(details):
    logging.debug("Backing off {wait:0.1f} seconds afters {tries} tries "
           "calling function {target} with args {args} and kwargs "
           "{kwargs}".format(**details))

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.Timeout,
                       requests.exceptions.ConnectionError,
                       requests.exceptions.MissingSchema,
                       requests.exceptions.RequestException,
                       requests.exceptions.HTTPError),
                      max_tries=5,
                      on_backoff=backoff_hdlr)

def retry_post(request,server):
    response = requests.request("POST", server)
    if response.status_code != 201:
        response.raise_for_status()
    else:
        load.addpost(server)
    return


#Test of basic request information from first server
def r_test(request):
    r = requests.get(servers[0])
    logging.debug (r.status_code,r.headers['content-type'],r.encoding,r.text)
    return request.Response(text=r.text)

#Return hello_world
def hello(request):
    return request.Response(text='Hello world!')


def get_server(request):
    #Get Next servers Information
    last=load.getRR()
    up_thread= threading.Thread(target= load.addRR)
    up_thread.start()
    server=servers[last]
    url = server #+"/1"
    try:
        response=requests.get(url)
    except Exception as e:
        logging.error ('Error with URL: '+url +str(e))
        return request.Response(text="Problem with server please retry")
    if response:
        logging.debug("nextRR"+str(last))
        load.addget(server)
        return request.Response(text=response.text)
    '''If we want to do somesort of automatic retries
    elif getRetry<MAXRETRY:
        get_server(request)'''

def sync_post(request,serverList): #sync post to other server without reply
    for server in serverList:
        logging.debug("Sync Posts started to server: "+str(server))
        retry_post(request,server)
    return

def sync_post_th(request,serverList): #sync post to other server without reply with multiple threads
    for server in serverList:
        logging.debug ("Sync Posts started to server: "+str(server))
        post_thread= threading.Thread(target=retry_post, args=(request,server))
        post_thread.start()
        logging.debug(str(post_thread))
    return

def post_server(request):
    firstSucc=0
    ser_len=load.len()
    for i in range(0,ser_len):
        server=load.getSer(i)
        response = requests.request("POST", server)
        if response.status_code == 201:
            logging.debug ("response from "+server+" num: " +str(i)+" "+response.text)
            load.addpost(server)
            if i<ser_len-1:
                postall_thread= threading.Thread(target=sync_post_th, args=(request,servers[i+1:]))
                postall_thread.start()
                logging.info ("Thread for all posts created",str(postall_thread))
            if firstSucc==0:
                firstSucc=1
                return request.Response(text=response.text)
        else:
            post_thread= threading.Thread(target=retry_post, args=(request,server))

app = Application()
#stat_thread= threading.Thread(target=log_stats)
#stat_thread.start()

servers=['https://jsonplaceholder.typicode.com/posts','https://tt','https://jsonplaceholder.typicode.com/posts']

logging.info("Start App on server list: " +str(servers))
load= loadB(servers)
app.router.add_route('/rtest', r_test, methods=['GET'])
app.router.add_route('/test', hello, methods=['GET'])
app.router.add_route('/', get_server, methods=['GET'])
app.router.add_route('/', post_server, methods=['POST'])
app.run(debug=False)
