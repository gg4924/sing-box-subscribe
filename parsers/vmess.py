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
    content = item.get('ps').strip() if item.get('ps') else tool.genName()
    node = {
        'tag': content,
        'type': 'vmess',
        'server': item.get('add'),
        'server_port': int(item.get('port')),
        'uuid': item.get('id'),
        'security': item.get('scy') if item.get('scy') else 'auto',
        'alter_Id': int(item.get('aid')),
        'packet_encoding': 'xudp'
    }
    if item.get('tls') and item['tls'] != '':
        node['tls']={
            'enabled': True,
            'insecure': True,
            'server_name': item.get('host', '')
        }
        if item.get('sni'):
            node['tls']['server_name'] = item['sni']
            node['tls']['utls'] = {
                'enabled': True,
                'fingerprint': item.get('fp', '')
            }
    if item.get("net"):
        if item['net'] == 'hs':
            node['transport'] = {
                'type':'http'
            }
            if item.get('host'):
                node['transport']['host'] = item['host'].split(',')[0]
            if item.get('path'):
                node['transport']['path'] = item['path'].rsplit("?")[0]
        if item['net'] == 'ws':
            node['transport'] = {
                'type':'ws',
                'path':item.get('path', '').rsplit("?")[0],
                'headers': {
                'Host': item.get('host', '')
                }
            }
        if item['net'] == 'quic':
            node['transport'] = {
                'type':'quic'
            }
        if item['net'] == 'grpc':
            node['transport'] = {
                'type':'grpc',
                'service_name':item.get('path', '')
            }
    return node
