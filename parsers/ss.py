import tool,json,re,urllib,sys
from urllib.parse import parse_qs
def parse(data):
    param = data[5:]
    if not param or param.isspace():
        return None
    node = {
        'tag':tool.genName()+'_shadowsocks',
        'type':'shadowsocks',
        'server':None,
        'server_port':0,
        'method':None,
        'password':None
    }
    flag = 0
    if param.find('#') > -1:
        if param[param.find('#') + 1:] != '':
            remark = urllib.parse.unquote(param[param.find('#') + 1:])
            node['tag'] = remark
        param = param[:param.find('#')]
    if param.find('plugin=obfs-local') > -1 or param.find('plugin=simple-obfs') > -1:
        plugin_opts={}
        if param.find('&', param.find('plugin')) > -1:
            plugin = urllib.parse.unquote(param[param.find('plugin'):param.find('&', param.find('plugin'))])
        else:
            plugin = urllib.parse.unquote(param[param.find('plugin'):])
        param = param[:param.find('?')]
        node['plugin'] = 'obfs-local'
        for p in plugin.split(';'):
            key_value = p.split('=')
            kname = key_value[0]
            pdict = {'obfs':'mode','obfs-host':'host'}
            if kname in pdict.keys():
                #kname = pdict[kname]
                plugin_opts[kname] = key_value[1]
        node['plugin_opts']=re.sub(r"\{|\}|\"|\\|\&|\s+", "", json.dumps(plugin_opts).replace(':','=', 2).replace(',',';').replace('Host','').replace('group',''))
    if param.find('v2ray-plugin') > -1:
        plugin_opts={}
        if param.find('&', param.find('v2ray-plugin')) > -1:
            plugin = tool.b64Decode(param[param.find('v2ray-plugin')+13:param.find('&', param.find('v2ray-plugin'))]).decode('utf-8')
        else:
            plugin = tool.b64Decode(param[param.find('v2ray-plugin')+13:]).decode('utf-8')
        param = param[:param.find('?')]
        node['plugin'] = 'v2ray-plugin'
        plugin = eval(plugin.replace('true','1'))
        result_str = "mode={};host={};{}{}{}{}".format(
            plugin.get("mode", ''),
            plugin.get("host", ''),
            'path={};'.format(plugin["path"]) if "path" in plugin else '',
            'mux={};'.format(plugin["mux"]) if "mux" in plugin else '',
            'headers={};'.format(json.dumps(plugin["headers"])) if "headers" in plugin else '',
            'fingerprint={};'.format(plugin["fingerprint"]) if "fingerprint" in plugin else ''
        )
        node['plugin_opts'] = result_str
    param2 = data[5:]
    if param2.find('shadow-tls') > -1:
        flag = 1
        if param.find('&', param.find('shadow-tls')) > -1:
            plugin = tool.b64Decode(param2[param2.find('shadow-tls')+11:param2.find('&', param2.find('shadow-tls'))].split('#')[0]).decode('utf-8')
        else:
            plugin = tool.b64Decode(param2[param2.find('shadow-tls')+11:].split('#')[0]).decode('utf-8')
        plugin = eval(plugin.replace('true','True'))
        node['detour'] = node['tag']+'_shadowtls'
        node_tls = {
            'tag':node['detour'],
            'type':'shadowtls',
            'version':int(plugin.get('version', '1')),
            'password':plugin.get('password', ''),
            'tls':{
                'enabled': True,
                'server_name': plugin.get('host', '')
            }
        }
        if plugin.get('address'):
            node_tls['server'] = plugin['address']
        if plugin.get('port'):
            node_tls['server_port'] = int(plugin['port'])
        if plugin.get('fp'):
            node_tls['tls']['utls']={
                'enabled': True,
                'fingerprint': plugin.get('fp')
            }
    if data[5:].find('protocol') > -1:
        smux = data[5:][data[5:].find('protocol'):]
        smux_dict = parse_qs(smux)
        smux_dict = {k: v[0] for k, v in smux_dict.items() if v[0]}
        node['multiplex'] = {
            'enabled': True,
            'protocol': smux_dict['protocol'],
            'max_streams': int(smux_dict.get('max-streams', '0'))
        }
        if smux_dict.get('max-connections'):
            node['multiplex']['max_connections'] = int(smux_dict['max-connections'])
        if smux_dict.get('min-streams'):
            node['multiplex']['min_streams'] = int(smux_dict['min-streams'])
        if smux_dict.get('padding') == 'True':
            node['multiplex']['padding'] = True
    if param.find('@') > -1:
        matcher = re.match(r'(.*?)@(.*):(.*)', param)
        if matcher:
            param = matcher.group(1)
            node['server'] = matcher.group(2)
            node['server_port'] = matcher.group(3).split('&')[0]
        else:
            return None
        try:
          matcher = re.match(r'(.*?):(.*)', tool.urlDecode(param).decode('utf-8'))
          if matcher:
              node['method'] = matcher.group(1)
              node['password'] = matcher.group(2)
          else:
              return None
        except:
          matcher = re.match(r'(.*?):(.*)', param)
          if matcher:
              node['method'] = matcher.group(1)
              node['password'] = matcher.group(2)
          else:
              return None
    else:
        matcher = re.match(r'(.*?):(.*)@(.*):(.*)', tool.urlDecode(param).decode('utf-8'))
        if matcher:
            node['method'] = matcher.group(1)
            node['password'] = matcher.group(2)
            node['server'] = matcher.group(3)
            node['server_port'] = matcher.group(4).split('&')[0]
        else:
            return None
    node['server_port'] = int(re.search(r'\d+', node['server_port']).group())
    if flag:
        return node,node_tls
    else:
        return node
