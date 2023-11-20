import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[8:]
    if not info or info.isspace():
        return None
    try:
        if info.find('?') > -1: #fuck奇葩的URI格式
            server_info = urlparse(info)
            netquery = dict(
                (k, v if len(v) > 1 else v[0])
                for k, v in parse_qs(server_info.query).items()
            )
            _path = tool.b64Decode(server_info.path).decode('utf-8').split("@")
            node = {
                'tag': netquery.get('remarks', tool.genName()+'_vmess'),
                'type': 'vmess',
                'server': _path[1].split(":")[0],
                'server_port': int(_path[1].split(":")[1]),
                'uuid': _path[0].split(":")[1],
                'security': _path[0].split(":")[0],
                'alter_Id': int(netquery.get('alterId','99')),
                'packet_encoding': 'xudp'
            }
            if netquery.get('tls') and netquery['tls'] != '':
                node['tls']={
                    'enabled': True,
                    'insecure': True,
                    'server_name': netquery.get('peer', '')
                }
                if netquery.get('sni'):
                    node['tls']['server_name'] = netquery['sni']
                    node['tls']['utls'] = {
                        'enabled': True,
                        'fingerprint': netquery.get('fp', '')
                    }
            if netquery.get('obfs') == 'websocket':
                node['transport'] = {
                    'type': 'ws',
                    'path': netquery.get('path', '').rsplit("?")[0],
                    'headers': {
                        'Host': json.loads(netquery.get('obfsParam')).get('Host', '') if netquery.get('obfsParam') else ''
                    }
                }
            return node
        else:
            proxy_str = tool.b64Decode(info).decode('utf-8')
    except:
        print(info)
        return None
    try:
        item = json.loads(proxy_str)
    except:
        return None
    content = item.get('ps').strip() if item.get('ps') else tool.genName()+'_vmess'
    node = {
        'tag': content,
        'type': 'vmess',
        'server': item.get('add'),
        'server_port': int(item.get('port')),
        'uuid': item.get('id'),
        'security': item.get('scy') if item.get('scy') else 'auto',
        'alter_Id': int(item.get('aid','99')),
        'packet_encoding': 'xudp'
    }
    if node['security'] == 'gun':
        node['security'] = 'auto'
    if 'tls' in item and (item['tls'] != '' and item['tls'] != 'none'):
        node['tls']={
            'enabled': True,
            'insecure': True,
            'server_name': item.get('host', '') if item.get("net") not in ['h2', 'http'] else ''
        }
        if item.get('sni'):
            node['tls']['server_name'] = item['sni']
            node['tls']['utls'] = {
                'enabled': True,
                'fingerprint': item.get('fp', '')
            }
    if item.get("net"):
        if item['net'] in ['h2', 'http']:
            node['transport'] = {
                'type':'http'
            }
            if item.get('host'):
                node['transport']['host'] = item['host']
            if item.get('path'):
                if type(item.get('path')) == str:
                    node['transport']['path'] = item['path'].rsplit("?")[0]
                else:
                    node['transport']['method'] = 'GET'
                    node['transport']['path'] = item['path'][0]
        if item['net'] == 'ws':
            node['transport'] = {
                'type':'ws',
                'path':str(item.get('path', '')).rsplit("?")[0],
                'headers': {
                    'Host': item.get('host', '')
                }
            }
            if '?ed=' in str(item.get('path', '')):
                node['transport']['early_data_header_name'] = 'Sec-WebSocket-Protocol'
                node['transport']['max_early_data'] = int(item.get('path').rsplit("?ed=")[1])
        if item['net'] == 'quic':
            node['transport'] = {
                'type':'quic'
            }
        if item['net'] == 'grpc':
            node['transport'] = {
                'type':'grpc',
                'service_name':item.get('path', '')
            }
    if item.get('protocol'):
        node['multiplex'] = {
            'enabled': True,
            'protocol': item['protocol'],
            'max_streams': int(item.get('max_streams', '0'))
        }
        if item.get('max_connections'):
            node['multiplex']['max_connections'] = int(item['max_connections'])
        if item.get('min_streams'):
            node['multiplex']['min_streams'] = int(item['min_streams'])
        if item.get('padding') == True:
            node['multiplex']['padding'] = True
    return node
