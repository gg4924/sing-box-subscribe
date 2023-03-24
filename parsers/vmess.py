import tool,json,re,urllib,sys
def parse(data):
    info = data[8:]
    if not info or info.isspace():
        return None
    #print(info)
    try:
        proxy_str = tool.b64Decode(info).decode('utf-8')
    except:
        print(info)
        return None
    item = json.loads(proxy_str)
    node = {
        'tag': item.get('ps').strip() if item.get('ps') else tool.genName(),
        'type': 'vmess',
        'server': item.get('add'),
        'server_port': int(item.get('port')),
        'uuid': item.get('id'),
        'security': item.get('scy') if item.get('scy') else 'auto',
        'alter_Id': int(item.get('aid'))
    }
    if item.get('tls'):
        node['tls']={
            'enabled': True
        }
        if item.get('sni'):
            node['tls']['disable_sni'] = False
            node['tls']['server_name'] = item['sni']
    if item.get("net"):
        if item['net']=='tcp':
            node['network'] = 'tcp'
        if item['net'] in ['tcp','hs']:
            node['transport'] = {
                'type':'http'
            }
            if item.get('host'):
                node['transport']['host'] = item['host'].split(',')
            if item.get('path'):
                node['transport']['path'] = item['path']
        if item['net'] == 'ws':
            node['transport'] = {
                'type':'ws'
            }
            if item.get('path'):
                node['transport']['path'] = item['path']
        if item['net'] == 'quic':
            node['transport'] = {
                'type':'quic'
            }
        if item['net'] == 'grpc' and item.get('serverName'):
            node['transport'] = {
                'type':'grpc',
                'service_name':item['serverName']
            }
    return node