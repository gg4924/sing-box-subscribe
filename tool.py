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
    '🇲🇴': re.compile(r'澳门|澳門|(?<=[\s-])MO(?=[\s-])|CTM|MAC|Macao|Macau'),
    '🇸🇬': re.compile(r'新加坡|狮城|獅城|沪新|京新|泉新|穗新|深新|杭新|广新|廣新|滬新|SG|Singapore|SINGAPORE'),
    '🇯🇵': re.compile(r'日本|东京|大阪|埼玉|京日|苏日|沪日|上日|穗日|川日|中日|泉日|杭日|深日|辽日|广日|JP|Japan|JAPAN'),
    '🇺🇸': re.compile(r'美国|京美|硅谷|凤凰城|洛杉矶|西雅图|芝加哥|哥伦布|纽约|(?<=[\s-])US(?=[\s-])|USA|America|United States'),
    '🇰🇷': re.compile(r'韩国|首尔|韩|韓|春川|KOR|KR|Korea'),
    '🇰🇵': re.compile(r'朝鲜|KP|North Korea'),
    '🇷🇺': re.compile(r'俄罗斯|毛子|俄国|RU|RUS|Russia'),
    '🇮🇳': re.compile(r'印度|孟买|IN|IND|India|INDIA|Mumbai'),
    '🇮🇩': re.compile(r'印尼|印度尼西亚|雅加达|ID|IDN|Indonesia'),
    '🇬🇧': re.compile(r'英国|伦敦|UK|England|United Kingdom|Britain'),
    '🇩🇪': re.compile(r'德国|德國|法兰克福|(?<=[\s-])DE(?=[\s-])|German|GERMAN'),
    '🇫🇷': re.compile(r'法国|法國|巴黎|FR|France'),
    '🇨🇳': re.compile(r'中国|中國|江苏|北京|上海|广州|深圳|杭州|徐州|青岛|宁波|镇江|沈阳|济南|回国|back|CN|China'),
    '🇩🇰': re.compile(r'丹麦|丹麥|DK|DNK|Denmark'),
    '🇳🇴': re.compile(r'挪威|(?<=[\s-])NO(?=[\s-])|Norway'),
    '🇮🇹': re.compile(r'意大利|義大利|米兰|(?<=[\s-])IT(?=[\s-])|Italy|Nachash'),
    '🇻🇦': re.compile(r'梵蒂冈|梵蒂岡|(?<=[\s-])VA(?=[\s-])|Vatican City'),
    '🇧🇪': re.compile(r'比利时|比利時|(?<=[\s-])BE(?=[\s-])|Belgium'),
    '🇦🇺': re.compile(r'澳大利亚|澳洲|墨尔本|悉尼|(?<=[\s-])AU(?=[\s-])|Australia|Sydney'),
    '🇨🇦': re.compile(r'加拿大|蒙特利尔|温哥华|多伦多|滑铁卢|楓葉|枫叶|CA|CAN|Waterloo|Canada|CANADA'),
    '🇲🇾': re.compile(r'马来西亚|马来|馬來|MY|Malaysia|MALAYSIA'),
    '🇲🇻': re.compile(r'马尔代夫|馬爾代夫|(?<=[\s-])MV(?=[\s-])|Maldives'),
    '🇹🇷': re.compile(r'土耳其|伊斯坦布尔|TR|TR-|TR_|TUR|Turkey'),
    '🇵🇭': re.compile(r'菲律宾|菲律賓|(?<=[\s-])PH(?=[\s-])|Philippines'),
    '🇹🇭': re.compile(r'泰国|泰國|曼谷|(?<=[\s-])TH(?=[\s-])|Thailand'),
    '🇻🇳': re.compile(r'越南|胡志明市|(?<=[\s-])VN(?=[\s-])|Vietnam'),
    '🇰🇭': re.compile(r'柬埔寨|(?<=[\s-])KH(?=[\s-])|Cambodia'),
    '🇱🇦': re.compile(r'老挝|(?<=[\s-])LA(?=[\s-])|Laos'),
    '🇧🇩': re.compile(r'孟加拉|(?<=[\s-])BD(?=[\s-])|Bengal'),
    '🇲🇲': re.compile(r'缅甸|緬甸|(?<=[\s-])MM(?=[\s-])|Myanmar'),
    '🇱🇧': re.compile(r'黎巴嫩|(?<=[\s-])LB(?=[\s-])|Lebanon'),
    '🇺🇦': re.compile(r'乌克兰|烏克蘭|(?<=[\s-])UA(?=[\s-])|Ukraine'),
    '🇭🇺': re.compile(r'匈牙利|(?<=[\s-])HU(?=[\s-])|Hungary'),
    '🇨🇭': re.compile(r'瑞士|苏黎世|(?<=[\s-])CH(?=[\s-])|Switzerland'),
    '🇸🇪': re.compile(r'瑞典|SE|Sweden'),
    '🇱🇺': re.compile(r'卢森堡|(?<=[\s-])LU(?=[\s-])|Luxembourg'),
    '🇦🇹': re.compile(r'奥地利|奧地利|维也纳|(?<=[\s-])AT(?=[\s-])|Austria'),
    '🇨🇿': re.compile(r'捷克|(?<=[\s-])CZ(?=[\s-])|Czechia'),
    '🇬🇷': re.compile(r'希腊|希臘|(?<=[\s-])GR(?=[\s-])|Greece'),
    '🇮🇸': re.compile(r'冰岛|冰島|(?<=[\s-])IS(?=[\s-])|ISL|Iceland'),
    '🇳🇿': re.compile(r'新西兰|新西蘭|(?<=[\s-])NZ(?=[\s-])|New Zealand'),
    '🇮🇪': re.compile(r'爱尔兰|愛爾蘭|都柏林|(?<=[\s-])IE(?=[\s-])|Ireland|IRELAND'),
    '🇮🇲': re.compile(r'马恩岛|馬恩島|(?<=[\s-])IM(?=[\s-])|Mannin|Isle of Man'),
    '🇱🇹': re.compile(r'立陶宛|(?<=[\s-])LT(?=[\s-])|Lithuania'),
    '🇫🇮': re.compile(r'芬兰|芬蘭|赫尔辛基|(?<=[\s-])FI(?=[\s-])|Finland'),
    '🇦🇷': re.compile(r'阿根廷|(?<=[\s-])AR(?=[\s-])|Argentina'),
    '🇺🇾': re.compile(r'乌拉圭|烏拉圭|(?<=[\s-])UY(?=[\s-])|Uruguay'),
    '🇵🇾': re.compile(r'巴拉圭|(?<=[\s-])PY(?=[\s-])|Paraguay'),
    '🇯🇲': re.compile(r'牙买加|牙買加|(?<=[\s-])JM(?=[\s-])|Jamaica'),
    '🇸🇷': re.compile(r'苏里南|蘇里南|(?<=[\s-])SR(?=[\s-])|Suriname'),
    '🇨🇼': re.compile(r'库拉索|庫拉索|(?<=[\s-])CW(?=[\s-])|Curaçao'),
    '🇨🇴': re.compile(r'哥伦比亚|(?<=[\s-])CO(?=[\s-])|Colombia'),
    '🇪🇨': re.compile(r'厄瓜多尔|(?<=[\s-])EC(?=[\s-])|Ecuador'),
    '🇪🇸': re.compile(r'西班牙|(?<=[\s-])ES(?=[\s-])|Spain'),
    '🇵🇹': re.compile(r'葡萄牙|(?<=[\s-])PT(?=[\s-])|Portugal'),
    '🇮🇱': re.compile(r'以色列|(?<=[\s-])IL(?=[\s-])|Israel'),
    '🇸🇦': re.compile(r'沙特|利雅得|吉达|Saudi|Saudi Arabia'),
    '🇲🇳': re.compile(r'蒙古|(?<=[\s-])MN(?=[\s-])|Mongolia'),
    '🇦🇪': re.compile(r'阿联酋|迪拜|(?<=[\s-])AE(?=[\s-])|Dubai|United Arab Emirates'),
    '🇦🇿': re.compile(r'阿塞拜疆|(?<=[\s-])AZ(?=[\s-])|Azerbaijan'),
    '🇦🇲': re.compile(r'亚美尼亚|亞美尼亞|(?<=[\s-])AM(?=[\s-])|Armenia'),
    '🇰🇿': re.compile(r'哈萨克斯坦|哈薩克斯坦|(?<=[\s-])KZ(?=[\s-])|Kazakhstan'),
    '🇰🇬': re.compile(r'吉尔吉斯坦|吉尔吉斯斯坦|(?<=[\s-])KG(?=[\s-])|Kyrghyzstan'),
    '🇺🇿': re.compile(r'乌兹别克斯坦|烏茲別克斯坦|(?<=[\s-])UZ(?=[\s-])|Uzbekistan'),
    '🇧🇷': re.compile(r'巴西|圣保罗|维涅杜|BR|Brazil'),
    '🇨🇱': re.compile(r'智利|(?<=[\s-])CL(?=[\s-])|Chile|CHILE'),
    '🇵🇪': re.compile(r'秘鲁|祕魯|(?<=[\s-])PE(?=[\s-])|Peru'),
    '🇨🇺': re.compile(r'古巴|(?<=[\s-])CU(?=[\s-])|Cuba'),
    '🇧🇹': re.compile(r'不丹|(?<=[\s-])BT(?=[\s-])|Bhutan'),
    '🇦🇩': re.compile(r'安道尔|(?<=[\s-])AD(?=[\s-])|Andorra'),
    '🇲🇹': re.compile(r'马耳他|(?<=[\s-])MT(?=[\s-])|Malta'),
    '🇲🇨': re.compile(r'摩纳哥|摩納哥|(?<=[\s-])MC(?=[\s-])|Monaco'),
    '🇷🇴': re.compile(r'罗马尼亚|(?<=[\s-])RO(?=[\s-])|Rumania'),
    '🇧🇬': re.compile(r'保加利亚|保加利亞|(?<=[\s-])BG(?=[\s-])|Bulgaria'),
    '🇭🇷': re.compile(r'克罗地亚|克羅地亞|(?<=[\s-])HR(?=[\s-])|Croatia'),
    '🇲🇰': re.compile(r'北马其顿|北馬其頓|(?<=[\s-])MK(?=[\s-])|North Macedonia'),
    '🇷🇸': re.compile(r'塞尔维亚|塞爾維亞|(?<=[\s-])RS(?=[\s-])|Seville|Sevilla'),
    '🇨🇾': re.compile(r'塞浦路斯|(?<=[\s-])CY(?=[\s-])|Cyprus'),
    '🇱🇻': re.compile(r'拉脱维亚|(?<=[\s-])LV(?=[\s-])|Latvia|Latvija'),
    '🇲🇩': re.compile(r'摩尔多瓦|摩爾多瓦|(?<=[\s-])MD(?=[\s-])|Moldova'),
    '🇸🇰': re.compile(r'斯洛伐克|(?<=[\s-])SK(?=[\s-])|Slovakia'),
    '🇪🇪': re.compile(r'爱沙尼亚|(?<=[\s-])EE(?=[\s-])|Estonia'),
    '🇧🇾': re.compile(r'白俄罗斯|白俄羅斯|(?<=[\s-])BY(?=[\s-])|White Russia|Republic of Belarus|Belarus'),
    '🇧🇳': re.compile(r'文莱|汶萊|BRN|Negara Brunei Darussalam'),
    '🇬🇺': re.compile(r'关岛|關島|(?<=[\s-])GU(?=[\s-])|Guam'),
    '🇫🇯': re.compile(r'斐济|斐濟|(?<=[\s-])FJ(?=[\s-])|Fiji'),
    '🇯🇴': re.compile(r'约旦|約旦|(?<=[\s-])JO(?=[\s-])|Jordan'),
    '🇬🇪': re.compile(r'格鲁吉亚|格魯吉亞|(?<=[\s-])GE(?=[\s-])|Georgia'),
    '🇬🇮': re.compile(r'直布罗陀|直布羅陀|(?<=[\s-])GI(?=[\s-])|Gibraltar'),
    '🇸🇲': re.compile(r'圣马力诺|聖馬利諾|(?<=[\s-])SM(?=[\s-])|San Marino'),
    '🇳🇵': re.compile(r'尼泊尔|(?<=[\s-])NP(?=[\s-])|Nepal'),
    '🇫🇴': re.compile(r'法罗群岛|法羅群島|(?<=[\s-])FO(?=[\s-])|Faroe Islands'),
    '🇦🇽': re.compile(r'奥兰群岛|奧蘭群島|(?<=[\s-])AX(?=[\s-])|Åland'),
    '🇸🇮': re.compile(r'斯洛文尼亚|斯洛文尼亞|(?<=[\s-])SI(?=[\s-])|Slovenia'),
    '🇦🇱': re.compile(r'阿尔巴尼亚|阿爾巴尼亞|(?<=[\s-])AL(?=[\s-])|Albania'),
    '🇹🇱': re.compile(r'东帝汶|東帝汶|(?<=[\s-])TL(?=[\s-])|East Timor'),
    '🇵🇦': re.compile(r'巴拿马|巴拿馬|(?<=[\s-])PA(?=[\s-])|Panama'),
    '🇧🇲': re.compile(r'百慕大|(?<=[\s-])BM(?=[\s-])|Bermuda'),
    '🇬🇱': re.compile(r'格陵兰|格陵蘭|(?<=[\s-])GL(?=[\s-])|Greenland'),
    '🇨🇷': re.compile(r'哥斯达黎加|(?<=[\s-])CR(?=[\s-])|Costa Rica'),
    '🇻🇬': re.compile(r'英属维尔京|(?<=[\s-])VG(?=[\s-])|British Virgin Islands'),
    '🇻🇮': re.compile(r'美属维尔京|(?<=[\s-])VI(?=[\s-])|United States Virgin Islands'),
    '🇲🇽': re.compile(r'墨西哥|MX|MEX|MEX|MEXICO'),
    '🇲🇪': re.compile(r'黑山|(?<=[\s-])ME(?=[\s-])|Montenegro'),
    '🇳🇱': re.compile(r'荷兰|荷蘭|尼德蘭|阿姆斯特丹|NL|Netherlands'),
    '🇵🇱': re.compile(r'波兰|波蘭|(?<=[\s-])PL(?=[\s-])|POL|Poland'),
    '🇩🇿': re.compile(r'阿尔及利亚|(?<=[\s-])DZ(?=[\s-])|Algeria'),
    '🇧🇦': re.compile(r'波黑共和国|波黑|(?<=[\s-])BA(?=[\s-])|Bosnia and Herzegovina'),
    '🇱🇮': re.compile(r'列支敦士登|(?<=[\s-])LI(?=[\s-])|Liechtenstein'),
    '🇷🇪': re.compile(r'留尼汪|留尼旺|(?<=[\s-])RE(?=[\s-])|Réunion|Reunion'),
    '🇿🇦': re.compile(r'南非|约翰内斯堡|(?<=[\s-])ZA(?=[\s-])|South Africa|Johannesburg'),
    '🇪🇬': re.compile(r'埃及|(?<=[\s-])EG(?=[\s-])|Egypt'),
    '🇬🇭': re.compile(r'加纳|(?<=[\s-])GH(?=[\s-])|Ghana'),
    '🇲🇦': re.compile(r'摩洛哥|(?<=[\s-])MA(?=[\s-])|Morocco'),
    '🇹🇳': re.compile(r'突尼斯|(?<=[\s-])TN(?=[\s-])|Tunisia'),
    '🇱🇾': re.compile(r'利比亚|(?<=[\s-])LY(?=[\s-])|Libya'),
    '🇰🇪': re.compile(r'肯尼亚|肯尼亞|(?<=[\s-])KE(?=[\s-])|Kenya'),
    '🇷🇼': re.compile(r'卢旺达|盧旺達|(?<=[\s-])RW(?=[\s-])|Rwanda'),
    '🇨🇻': re.compile(r'佛得角|維德角|(?<=[\s-])CV(?=[\s-])|Cape Verde'),
    '🇦🇴': re.compile(r'安哥拉|(?<=[\s-])AO(?=[\s-])|Angola'),
    '🇳🇬': re.compile(r'尼日利亚|尼日利亞|拉各斯|(?<=[\s-])NG(?=[\s-])|Nigeria'),
    '🇲🇺': re.compile(r'毛里求斯|(?<=[\s-])MU(?=[\s-])|Mauritius'),
    '🇴🇲': re.compile(r'阿曼|(?<=[\s-])OM(?=[\s-])|Oman'),
    '🇧🇭': re.compile(r'巴林|(?<=[\s-])BH(?=[\s-])|Bahrain'),
    '🇮🇶': re.compile(r'伊拉克|(?<=[\s-])IQ(?=[\s-])|Iraq'),
    '🇮🇷': re.compile(r'伊朗|(?<=[\s-])IR(?=[\s-])|Iran'),
    '🇦🇫': re.compile(r'阿富汗|(?<=[\s-])AF(?=[\s-])|Afghanistan'),
    '🇵🇰': re.compile(r'巴基斯坦|(?<=[\s-])PK(?=[\s-])|Pakistan|PAKISTAN'),
    '🇶🇦': re.compile(r'卡塔尔|卡塔爾|(?<=[\s-])QA(?=[\s-])|Qatar'),
    '🇸🇾': re.compile(r'叙利亚|敘利亞|(?<=[\s-])SY(?=[\s-])|Syria'),
    '🇱🇰': re.compile(r'斯里兰卡|斯里蘭卡|(?<=[\s-])LK(?=[\s-])|Sri Lanka'),
    '🇻🇪': re.compile(r'委内瑞拉|(?<=[\s-])VE(?=[\s-])|Venezuela'),
    '🇬🇹': re.compile(r'危地马拉|(?<=[\s-])GT(?=[\s-])|Guatemala'),
    '🇵🇷': re.compile(r'波多黎各|(?<=[\s-])PR(?=[\s-])|Puerto Rico'),
    '🇰🇾': re.compile(r'开曼群岛|開曼群島|盖曼群岛|凯门群岛|(?<=[\s-])KY(?=[\s-])|Cayman Islands'),
    '🇭🇳': re.compile(r'洪都拉斯|(?<=[\s-])HN(?=[\s-])|Honduras'),
    '🇳🇮': re.compile(r'尼加拉瓜|(?<=[\s-])NI(?=[\s-])|Nicaragua'),
    '🇦🇶': re.compile(r'南极|南極|(?<=[\s-])AQ(?=[\s-])|Antarctica'),
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
