import tool,json,re,urllib,sys
def parse(data):
    param = data[5:]
    if not param or param.isspace():
        return None
    node = {
        'tag':tool.genName(),
        'type':'shadowsocks',
        'server':None,
        'server_port':0,
        'method':None,
        'password':None
    }
    if param.find('#') > -1:
        remark = urllib.parse.unquote(param[param.find('#') + 1:])
        node['tag'] = tool.rename(remark)
        param = param[:param.find('#')]
    if param.find('/?') > -1:
        plugin = urllib.parse.unquote(param[param.find('/?') + 2:])
        if plugin.startswith('plugin'):
            p1 = 0
            node['plugin'] = plugin.split(';',1)[0].split('=')[1]
        if plugin.startswith('v2ray-plugin'):
            p1 =1
            node['plugin'] = 'v2ray-plugin'
            plugin = str(tool.b64Decode(plugin.split('=')[1]),'utf-8')
        plugin_opts={}
        param = param[:param.find('/?')]
        if p1 == 0 :
            for p in plugin.split(';'):
                key_value = p.split('=')
                kname = key_value[0]
                pdict = {'obfs':'mode','obfs-host':'host'}
                if kname in pdict.keys():
                    #kname = pdict[kname]
                    plugin_opts[kname] = key_value[1]
        if p1 == 1 :
            plugin = eval(plugin.replace('true','1'))
            for kname in plugin.keys():
                pdict = {'mode':'obfs','host':'obfs-host'}
                if kname in pdict.keys():
                    #kname = pdict[kname]
                    plugin_opts[kname] = plugin[kname]
        node['plugin_opts']=re.sub(r"\{|\}|\"|\\|\:|\&|\s+", "", json.dumps(plugin_opts).replace(':','=', 2).replace(',',';').replace('Host','').replace('group',''))
    if param.find('@') > -1:
        matcher = re.match(r'(.*?)@(.*):(.*)', param)
        if matcher:
            param = matcher.group(1)
            node['server'] = matcher.group(2)
            node['server_port'] = matcher.group(3)
        else:
            return None
        matcher = re.match(r'(.*?):(.*)', tool.urlDecode(param).decode('utf-8'))
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
            node['server_port'] = matcher.group(4)
        else:
            return None
    node['server_port'] = int(node['server_port'])
    return node
