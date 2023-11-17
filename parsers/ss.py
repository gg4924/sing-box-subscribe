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
    if param.find('/?') > -1:
        plugin_opts={}
        plugin = urllib.parse.unquote(param[param.find('/?') + 2:])
        param = param[:param.find('/?')]
        if plugin.startswith('plugin'):
            if 'obfs' in plugin.split(';',1)[0].split('=')[1]:
                node['plugin'] = 'obfs-local'
            for p in plugin.split(';'):
                key_value = p.split('=')
                kname = key_value[0]
                pdict = {'obfs':'mode','obfs-host':'host'}
                if kname in pdict.keys():
                    #kname = pdict[kname]
                    plugin_opts[kname] = key_value[1]
            node['plugin_opts']=re.sub(r"\{|\}|\"|\\|\:|\&|\s+", "", json.dumps(plugin_opts).replace(':','=', 2).replace(',',';').replace('Host','').replace('group',''))
    if param.find('?') > -1 and param[param.find('?')-1] != '/':
        plugin_opts={}
        plugin = urllib.parse.unquote(param[param.find('?') + 1:])
        param = param[:param.find('?')]
        if plugin.startswith('v2ray-plugin'):
            node['plugin'] = 'v2ray-plugin'
            plugin = str(tool.b64Decode(plugin.split('=')[1]),'utf-8')
            plugin = eval(plugin.replace('true','1'))
            for kname in plugin.keys():
                pdict = {'mode':'obfs','host':'obfs-host'}
                if kname in pdict.keys():
                    #kname = pdict[kname]
                    plugin_opts[kname] = plugin[kname]
            node['plugin_opts']=re.sub(r"\{|\}|\"|\\|\:|\&|\s+", "", json.dumps(plugin_opts).replace(':','=', 2).replace(',',';'))
        elif plugin.startswith('shadow-tls'):
            flag = 1
            plugin = json.loads(tool.b64Decode(plugin.split("=", 1)[1]))
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
    if param.find('&') > -1:
        smux = param[param.find('&')+1:]
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
    node['server_port'] = int(node['server_port'])
    if flag:
        return node,node_tls
    else:
        return node
