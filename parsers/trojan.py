import tool,json,re,urllib,sys
def parse(data):
    node = {
        'tag':None,
        'type':'trojan',
        'server':None,
        'server_port':None,
        'password':None
    }
    if isinstance(data,bytes):
        data = bytes.decode(data)
    m = re.search(r'://(.+?)@(.+?):(\d+)',data)
    if m:
        node['password'] = urllib.parse.unquote(m.group(1))
        node['server'] =m.group(2)
        node['server_port'] =int(m.group(3))
    else:
        return None
    m = re.search(r'/?\?(.+?)#',data)
    if m:
        params = m.group(1)
        palist = params.split('&')
        opts = {}
        for kv in palist:
            k = kv.split('=')[0]
            v = urllib.parse.unquote(kv.split('=')[1])
            opts[k] = v
        node['tls']={}
        if opts.get('allowInsecure'):
            node['tls']={
                'enabled' : True,
                'insecure' : False
                }
            if(opts['allowInsecure']=='0'):
                node['tls']['insecure']=False
            else:
                node['tls']['insecure']=True
        if opts.get('sni'):
            node['tls']['enabled'] = True
            node['tls']['disable_sni'] = False
            node['tls']['server_name'] = opts['sni']
        if opts.get('type'):
            if opts['type'] == 'h2':
                node['transport']={
                    'type':'http',
                    'host':opts['host'] if opts.get['host'] else node['server'],
                    'path':opts['path'] if opts.get('path') else '/'
                }
            if opts['type'] == 'ws':
                node['transport']={
                    'type':'ws',
                    'path':opts['path'] if opts.get('path') else '/'
                }

    if data.find('#')>-1:
        name = urllib.parse.unquote(data[data.find('#')+1:])
        name = name.strip()
    else:
        name = tool.rename(tool.genName())
    node['tag'] = name
    return node
