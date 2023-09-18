import json,os,tool,time,requests,sys,urllib,re,importlib,argparse
from datetime import datetime
import tempfile
from api.app import TEMP_DIR

parsers_mod = {}
providers = None
color_code = [31,32,33,34,35,36,91,92,93,94,95,96]

def loop_color(text):
    text = '\033[1;{color}m{text}\033[0m'.format(color=color_code[0],text=text)
    color_code.append(color_code.pop(0))
    return text

def init_parsers():
    b = os.walk('parsers')
    for path,dirs,files in b:
        for file in files:
            f = os.path.splitext(file)
            if f[1] == '.py':
                parsers_mod[f[0]] = importlib.import_module('parsers.'+f[0])

def get_template():
    template_dir = 'config_template'  # 配置模板文件夹路径
    template_files = os.listdir(template_dir)  # 获取文件夹中的所有文件
    template_list = [os.path.splitext(file)[0] for file in template_files if file.endswith('.json')]  # 移除扩展名并过滤出以.json结尾的文件
    template_list.sort()  # 对文件名进行排序
    return template_list

def load_json(path):
    return json.loads(tool.readFile(path))

def process_subscribes(subscribes):
    nodes = {}
    for subscribe in subscribes:
        if 'enabled' in subscribe and not subscribe['enabled']:
            continue
        _nodes = get_nodes(subscribe['url'])
        if _nodes and len(_nodes) > 0:
            add_prefix(_nodes,subscribe)
            add_emoji(_nodes,subscribe)
            if not nodes.get(subscribe['tag']):
                nodes[subscribe['tag']] = []
            nodes[subscribe['tag']] += _nodes
        else:
            print('没有在此订阅下找到节点，跳过')
    tool.proDuplicateNodeName(nodes)
    return nodes

def nodes_filter(nodes,filter,group):
    for a in filter:
        if a.get('for') and group not in a['for']:
            continue
        nodes = action_keywords(nodes,a['action'],a['keywords'])
    return nodes

def action_keywords(nodes,action,keywords):
    # filter将按顺序依次执行
    # "filter":[
    #         {"action":"include","keywords":[""]},
    #         {"action":"exlude","keywords":[""]}
    #     ]
    temp_nodes = []
    flag = False
    if action == 'exlude':
        flag = True
    # 空关键字过滤
    _keywords = []
    for k in keywords:
        if k != "":
            _keywords.append(k)
    keywords = _keywords
    if len(keywords) == 0:
        return nodes
    for node in nodes:
        name = node['tag']
        match_flag = False
        for k in keywords:
            if k in name:
                match_flag = True
                break
        if match_flag ^ flag:
            temp_nodes.append(node)
    return temp_nodes

def add_prefix(nodes,subscribe):
    if subscribe.get('prefix'):
        for node in nodes:
            node['tag'] = subscribe['prefix']+node['tag']

def add_emoji(nodes,subscribe):
    if subscribe.get('emoji'):
        for node in nodes:
            node['tag'] = tool.rename(node['tag'])
            
def get_nodes(url):
    urlstr = urllib.parse.urlparse(url)
    if not urlstr.scheme:
        content = get_content_form_file(url)
    else:
        content = get_content_from_url(url)
    if content:
        data = parse_content(content)
        return data
    return None

def parse_content(content):
    # firstline = tool.firstLine(content)
    # # print(firstline)
    # if not get_parser(firstline):
    #     return None
    nodelist = []
    for t in content.splitlines():
        t = t.strip()
        if len(t)==0:
            continue
        factory = get_parser(t)
        if not factory:
            continue
        node = factory(t)
        if node:
            nodelist.append(node)
    return nodelist

def get_parser(node):
    proto = tool.get_protocol(node)
    if providers.get('exlude_protocol'):
        eps = providers['exlude_protocol'].split(',')
        if len(eps) > 0:
            eps = [protocol.strip() for protocol in eps]
            if proto in eps:
                return None
    if not proto or proto not in parsers_mod.keys():
        return None
    return parsers_mod[proto].parse

def get_content_from_url(url,n=6):
    print('处理'+url)
    response = tool.getResponse(url)
    concount = 1
    while concount <= n and not response:
        print('连接出错，正在进行第 '+str(concount)+' 次重试，最多重试 '+str(n)+' 次...')
        response = tool.getResponse(url)
        concount = concount+1
        time.sleep(1)
    if not response:
        print('获取错误，跳过此订阅')
        print('----------------------------')
        return None
    response_text = response.text
    response_encoding = response.encoding
    if response_text.isspace():
        print('没有从订阅链接获取到任何内容')
        return None
    try:
        response_text = tool.b64Decode(response_text)
        #response_text = response_text.decode(encoding="utf-8")
        response_text = bytes.decode(response_text,encoding=response_encoding)
    except:
        pass
        # traceback.print_exc()
    return response_text

def get_content_form_file(url):
    print('处理'+url)
    encoding = tool.get_encoding(url)
    data = tool.readFile(url)
    data = bytes.decode(data,encoding=encoding)
    data = tool.noblankLine(data)
    return data

def save_config(path,nodes):
    try:
        if 'auto_backup' in providers and providers['auto_backup']:
            now = datetime.now().strftime('%Y%m%d%H%M%S')
            if os.path.exists(path):
                os.rename(path, f'{path}.{now}.bak')
        tool.saveFile(path, json.dumps(nodes, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"保存配置文件时出错：{str(e)}")
        # 如果保存出错，尝试使用 config_file_path 再次保存
        try:
            config_path = json.loads(temp_json_data).get("save_config_path", "config.json")
            CONFIG_FILE_NAME = config_path
            config_file_path = os.path.join('/tmp', CONFIG_FILE_NAME)
            if os.path.exists(config_file_path):
                os.remove(config_file_path)
                print(f"已删除文件：{config_file_path}")
            else:
                print(f"文件不存在：{config_file_path}")
            tool.saveFile(config_file_path, json.dumps(nodes, indent=2, ensure_ascii=False))
            print(f"配置文件已保存到 {config_file_path}")
        except Exception as e:
            print(f"再次保存配置文件时出错：{str(e)}")

def set_proxy_rule_dns(config):
    # dns_template = {
    #     "tag": "remote",
    #     "address": "tls://1.1.1.1",
    #     "detour": ""
    # }
    config_rules = config['route']['rules']
    outbound_dns = []
    dns_rules = config['dns']['rules']
    asod = providers["auto_set_outbounds_dns"]
    for rule in config_rules:
        if rule['outbound'] not in ['block','dns-out']:
            if rule['outbound'] != 'direct':
                outbounds_dns_template = list(filter(lambda server:server['tag']==asod["proxy"],config['dns']['servers']))[0]
                dns_obj = outbounds_dns_template.copy()
                dns_obj['tag'] = rule['outbound']+'_dns'
                dns_obj['detour'] = rule['outbound']
                if dns_obj not in outbound_dns:
                    outbound_dns.append(dns_obj)
            if rule.get('type') and rule['type'] == 'logical':
                dns_rule_obj = {
                    'type':'logical',
                    'mode':rule['mode'],
                    'rules':[],
                    'server':rule['outbound']+'_dns' if rule['outbound'] != 'direct' else asod["direct"]
                }
                for _rule in rule['rules']:
                    child_rule = pro_dns_from_route_rules(_rule)
                    if child_rule:
                        dns_rule_obj['rules'].append(child_rule)
                if len(dns_rule_obj['rules']) == 0:
                    dns_rule_obj = None
            else:
                dns_rule_obj = pro_dns_from_route_rules(rule)
            if dns_rule_obj:
                dns_rules.append(dns_rule_obj)
    # 清除重复规则
    _dns_rules = []
    for dr in dns_rules:
        if dr not in _dns_rules:
            _dns_rules.append(dr)
    config['dns']['rules'] = _dns_rules
    config['dns']['servers'].extend(outbound_dns)

def pro_dns_from_route_rules(route_rule):
    dns_route_same_list = ["inbound","ip_version","network","protocol",'domain','domain_suffix','domain_keyword','domain_regex','geosite',"source_geoip","source_ip_cidr","source_port","source_port_range","port","port_range","process_name","process_path","package_name","user","user_id","clash_mode","invert"]
    dns_rule_obj = {}
    for key in route_rule:
        if key in dns_route_same_list:
            dns_rule_obj[key] = route_rule[key]
    if len(dns_rule_obj) == 0:
        return None
    if route_rule.get('outbound'):
        dns_rule_obj['server'] = route_rule['outbound']+'_dns' if route_rule['outbound'] != 'direct' else providers["auto_set_outbounds_dns"]['direct']
    return dns_rule_obj

def pro_node_template(data_nodes,config_outbound,group):
    if config_outbound.get('filter'):
        data_nodes = nodes_filter(data_nodes,config_outbound['filter'],group)
    return [node.get('tag') for node in data_nodes]

def combin_to_config(config,data):
    config_outbounds = config["outbounds"] if config.get("outbounds") else None
    temp_outbounds = []
    if config_outbounds:
        # 提前处理all模板
        for po in config_outbounds:
            # 处理出站
            if po.get("outbounds"):
                if '{all}' in po["outbounds"]:
                    o1 = []
                    for item in po["outbounds"]:
                        if item.startswith('{') and item.endswith('}'):
                            _item = item[1:-1]
                            if _item == 'all':
                                o1.append(item)
                        else:
                            o1.append(item)
                    po['outbounds'] = o1
                t_o = []
                check_dup = []
                for oo in po["outbounds"]:
                    # 避免添加重复节点
                    if oo in check_dup:
                        continue
                    else:
                        check_dup.append(oo)
                    # 处理模板
                    if oo.startswith('{') and oo.endswith('}'):
                        oo = oo[1:-1]
                        if data.get(oo):
                            nodes = data[oo]
                            t_o.extend(pro_node_template(nodes,po,oo))
                        else:
                            if oo == 'all':
                                for group in data:
                                    nodes = data[group]
                                    t_o.extend(pro_node_template(nodes,po,group))
                    else:
                        t_o.append(oo)
                if len(t_o)==0:
                    print('发现 {} 出站下的节点数量为 0 ，会导致sing-box无法运行，请检查config模板是否正确。'.format(po['tag']))
                    config_path = json.loads(temp_json_data).get("save_config_path", "config.json")
                    CONFIG_FILE_NAME = config_path
                    config_file_path = os.path.join('/tmp', CONFIG_FILE_NAME)
                    if os.path.exists(config_file_path):
                        os.remove(config_file_path)
                        print(f"已删除文件：{config_file_path}")
                    sys.exit()
                po['outbounds'] = t_o
                if po.get('filter'):
                    del po['filter']
    for group in data:
        temp_outbounds.extend(data[group])
    config['outbounds'] = config_outbounds+temp_outbounds
    # 自动配置路由规则到dns规则，避免dns泄露
    dns_tags = [server.get('tag') for server in config['dns']['servers']]
    asod = providers.get("auto_set_outbounds_dns")
    if asod and asod.get('proxy') and asod.get('direct') and asod['proxy'] in dns_tags and asod['direct'] in dns_tags:
        set_proxy_rule_dns(config)
    return config

def updateLocalConfig(local_host,path):
    header = {
        'Content-Type':'application/json'
    }
    r = requests.put(local_host+'/configs?force=false',json={"path":path},headers=header)
    print(r.text)

def display_template(tl):
    print_str = ''
    for i in range(len(tl)):
        print_str += loop_color('{index}、{name} '.format(index=i+1,name=tl[i]))
    print(print_str)

def select_config_template(tl, selected_template_index=None):
    if args.template_index is not None:
        uip = args.template_index
    else:
        uip = input('输入序号，载入对应config模板（直接回车默认选第一个配置模板）：')
        try:
            if uip == '':
                return 0
            uip = int(uip)
            if uip < 1 or uip > len(tl):
                print('输入了错误信息！重新输入')
                return select_config_template(tl)
            else:
                uip -= 1
        except:
            print('输入了错误信息！重新输入')
            return select_config_template(tl)

    return uip

# 自定义函数，用于解析参数为 JSON 格式
def parse_json(value):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise argparse.ArgumentTypeError(f"Invalid JSON: {value}")

if __name__ == '__main__':
    init_parsers()
    parser = argparse.ArgumentParser()
    parser.add_argument('--temp_json_data', type=parse_json, help='临时内容')
    parser.add_argument('--template_index', type=int, help='模板序号')
    args = parser.parse_args()
    temp_json_data = args.temp_json_data
    if temp_json_data and temp_json_data != '{}':
        providers = json.loads(temp_json_data)
    else:
        providers = load_json('providers.json')  # 加载本地 providers.json
    template_list = get_template()
    if len(template_list) < 1:
        print('没有找到模板文件')
        sys.exit()
    display_template(template_list)

    uip = select_config_template(template_list, selected_template_index=args.template_index)
    config_template_path = 'config_template/'+template_list[uip]+'.json'
    config = load_json(config_template_path)
    nodes = process_subscribes(providers["subscribes"])
    final_config = combin_to_config(config,nodes)
    save_config(providers["save_config_path"],final_config)
    # updateLocalConfig('http://127.0.0.1:9090',providers['save_config_path'])
