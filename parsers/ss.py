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
        if plugin.startswith('obfs'):
            node['plugin'] = 'obfs'
        node['plugin_opts']={}
        param = param[:param.find('/?')]
        for p in plugin.split(';'):
            key_value = p.split('=')
            kname = key_value[0]
            pdict = {'obfs':'mode','obfs-host':'host'}
            if kname in pdict.keys():
                kname = pdict[kname]
                node['plugin_opts'][kname] = key_value[1]
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
