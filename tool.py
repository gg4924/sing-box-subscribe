import urllib.parse,base64,requests,paramiko,random,string,re,chardet
from paramiko import SSHClient
from scp import SCPClient

def get_encoding(file):
    with open(file,'rb') as f:
        return chardet.detect(f.read())['encoding']
    
def saveFile(path,content):
    file = open(path, mode='w',encoding='utf-8')
    file.write(content)
    file.close()

regex_patterns = {
    '🇭🇰': re.compile(r'香港|深港|沪港|呼港|HKT|HKBN|HGC|WTT|CMI|穗港|京港|港|HK|Hongkong|Hong Kong|HongKong|HONG KONG'),
    '🇹🇼': re.compile(r'台湾|台北|台中|新北|彰化|台|CHT|HINET|TW|Taiwan|TAIWAN'),
    '🇸🇬': re.compile(r'新加坡|狮城|獅城|沪新|京新|泉新|穗新|深新|杭新|广新|廣新|滬新|SG|Singapore|SINGAPORE'),
    '🇯🇵': re.compile(r'日本|东京|大阪|埼玉|京日|苏日|沪日|上日|穗日|川日|中日|泉日|杭日|深日|辽日|广日|JP|Japan|JAPAN'),
    '🇺🇸': re.compile(r'美国|美|京美|硅谷|凤凰城|洛杉矶|西雅图|芝加哥|哥伦布|纽约|(?<=[\s-])US(?=[\s-])|USA|America|United States'),
    '🇰🇷': re.compile(r'韩国|首尔|韩|韓|春川|KOR|KR|Korea'),
    '🇷🇺': re.compile(r'俄罗斯|毛子|俄国|RU|RUS|Russia'),
    '🇮🇳': re.compile(r'印度|孟买|IN|IND|India|INDIA|Mumbai'),
    '🇬🇧': re.compile(r'英国|伦敦|英|UK|England|United Kingdom|Britain'),
    '🇩🇪': re.compile(r'德国|德國|法兰克福|(?<=[\s-])DE(?=[\s-])|German|GERMAN'),
    '🇫🇷': re.compile(r'法国|法國|巴黎|FR|France'),
    '🇮🇹': re.compile(r'意大利|義大利|米兰|(?<=[\s-])IT(?=[\s-])|Italy|Nachash'),
    '🇦🇺': re.compile(r'澳大利亚|澳洲|墨尔本|悉尼|(?<=[\s-])AU(?=[\s-])|Australia|Sydney'),
    '🇨🇦': re.compile(r'加拿大|蒙特利尔|温哥华|多伦多|滑铁卢|楓葉|枫叶|CA|CAN|Waterloo|Canada|CANADA'),
    '🇲🇾': re.compile(r'马来西亚|马来|馬來|MY|Malaysia|MALAYSIA'),
    '🇹🇷': re.compile(r'土耳其|伊斯坦布尔|TR|TR-|TR_|TUR|Turkey'),
    '🇻🇳': re.compile(r'越南|胡志明市|(?<=[\s-])VN(?=[\s-])|Vietnam'),
    '🇨🇭': re.compile(r'瑞士|苏黎世|(?<=[\s-])CH (?=[\s-])|Switzerland'),
    '🇸🇪': re.compile(r'瑞典|SE|Sweden'),
    '🇦🇷': re.compile(r'阿根廷|(?<=[\s-])AR(?=[\s-])|Argentina'),
    '🇮🇱': re.compile(r'以色列|(?<=[\s-])IL(?=[\s-])|Israel'),
    '🇸🇦': re.compile(r'沙特|利雅得|吉达|Saudi|Saudi Arabia'),
    '🇲🇳': re.compile(r'蒙古|(?<=[\s-])MN(?=[\s-])|Mongolia'),
    '🇦🇪': re.compile(r'阿联酋|迪拜|(?<=[\s-])AE(?=[\s-])|Dubai|United Arab Emirates'),
    '🇧🇷': re.compile(r'巴西|圣保罗|维涅杜|BR|Brazil'),
    '🇨🇱': re.compile(r'智利|Chile|CHILE'),
    '🇲🇽': re.compile(r'墨西哥|MX|MEX|MEX|MEXICO'),
    '🇳🇱': re.compile(r'荷兰|荷蘭|尼德蘭|阿姆斯特丹|NL|Netherlands'),
    '🇿🇦': re.compile(r'南非|约翰内斯堡|South Africa|Johannesburg'),
    '🇨🇳': re.compile(r'中国|中國|江苏|北京|上海|广州|深圳|杭州|徐州|青岛|宁波|镇江|回国|back|CN|China'),
}

def rename(input_str):
    for country_code, pattern in regex_patterns.items():
        if pattern.search(input_str) and not input_str.startswith(country_code):
            input_str = country_code + ' ' + input_str
            break
    return input_str

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


def proDuplicateNodeName(nodes):
    names = []
    for key in nodes.keys():
        nodelist = nodes[key]
        for node in nodelist:
            index = 1
            s = node['tag']
            while node['tag'] in names:
                node['tag'] = s+str(index)
                index += 1
            names.append(node['tag'])


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
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36'
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
