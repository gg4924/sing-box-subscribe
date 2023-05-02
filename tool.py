import urllib.parse,base64,requests,paramiko,random,string,re,chardet
from paramiko import SSHClient
from scp import SCPClient

def get_encoding(file):
    with open(file,'rb') as f:
        return chardet.detect(f.read())['encoding']
    
def saveFile(path,content):
    file = open(path,'w')
    file.write(content)
    file.close()


def urlDecode(str):
    str = str.strip()
    str += (len(str)%4)*'='
    return base64.urlsafe_b64decode(str)


def b64Decode(str):
    str = str.strip()
    str += (len(str)%4)*'='
    #print(str)
    return base64.b64decode(str)


def readFile(path):
    file = open(path,'rb')
    content = file.read()
    file.close()
    return content


def noblankLine(data):
    lines = data.splitlines()
    newdata = ''
    for index in range(len(lines)):
        line = lines[index]
        t = line.strip()
        if len(t)>0:
            newdata += t
            if index+1<len(lines):
                newdata += '\n'
    return newdata


def firstLine(data):
    lines = data.splitlines()
    for line in lines:
        line = line.strip()
        if line:
            return line


def genName(length=8):
    name = ''
    for i in range(length):
        name += random.choice(string.ascii_letters+string.digits)
    return name

def is_ip(str):
    return re.search(r'^\d+\.\d+\.\d+\.\d+$',str)

def get_protocol(str):
    m = re.search(r'^(.+?)://',str)
    if m:
        return m.group(1)
    return None

def checkKeywords(keywords,str):
    if not keywords:
        return False
    for keyword in keywords:
        if str.find(keyword)>-1:
            return True
    return False


def filterNodes(nodelist,keywords):
    newlist = []
    if not keywords:
        return nodelist
    for node in nodelist:
        if not checkKeywords(keywords,node['name']):
            newlist.append(node)
        else:
            print('过滤节点名称 '+node['name'])
    return newlist


def replaceStr(nodelist,keywords):
    if not keywords:
        return nodelist
    for node in nodelist:
        for k in keywords:
            node['name'] = node['name'].replace(k,'').strip()
    return nodelist


def proDuplicateNodeName(nodelist):
    names = []
    for node in nodelist:
        index = 0
        s = node['tag']
        while node['tag'] in names:
            node['tag'] = s+str(index)
            index += 1
        names.append(node['tag'])
    return nodelist


def removeNodes(nodelist):
    newlist = []
    temp_list=[]
    i=0
    for node in nodelist:
        _node = {'server':node['server'],'port':node['port']}
        if _node in temp_list:
            i+=1
        else:
            temp_list.append(_node)
            newlist.append(node)
    print('去除了 '+str(i)+' 个重复节点')
    print('实际获取 '+str(len(newlist))+' 个节点')
    return newlist


def prefixStr(nodelist,prestr):
    for node in nodelist:
        node['name'] = prestr+node['name'].strip()
    return nodelist



def getResponse(url):
    response = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url,headers=headers,timeout=5000)
        if response.status_code==200:
            return response
        else:
            return None
    except:
        return None
    
class ConfigSSH:
    server = {'ip':None,'port':22,'user':None,'password':''}
    def __init__(self,server:dict) -> None:
        for k in self.server:
            if k != 'port' and not k in server.keys():
                return None
            if k in server.keys():
                self.server[k] = server[k]
    def connect(self):
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self.server['ip'],port=22, username=self.server['user'], password=self.server['password'])
        self.ssh = ssh

    def execCMD(self,command:str):
        stdin, stdout, stderr = self.ssh.exec_command(command) 
        print(stdout.read().decode('utf-8')) 

    def uploadFile(self,source:str,target:str):
        scp = SCPClient(self.ssh.get_transport())
        scp.put(source, recursive=True, remote_path=target)

    def getFile(self,remote:str,local:str):
        scp = SCPClient(self.ssh.get_transport())
        scp.get(remote,local)

    def close(self):
        self.ssh.close()
