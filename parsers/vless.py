import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    _netloc = server_info.netloc.split("@")
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': unquote(server_info.fragment),
        'type': 'vless',
        'server': _netloc[1].split(":")[0],
        'server_port': int(_netloc[1].split(":")[1]),
        'uuid': _netloc[0],
        'flow': netquery.get('flow', ''),
        'packet_encoding': netquery.get('packetEncoding', 'xudp')
    }
    if netquery.get('security'):
        node['tls']={
            'enabled': True
        }
        if netquery.get('sni'):
            node['tls']['server_name'] = netquery['sni']
            node['tls']['utls'] = {
                'enabled': True,
                'fingerprint': netquery.get('fp', '')
            }
        if netquery['security'] == 'reality':
            node['tls']['reality'] = {
                'enabled': True,
                'public_key': netquery.get('pbk'),
                'short_id': netquery.get('sid', '')
            }
    if netquery.get('type'):
        if netquery['type'] in ['tcp','http']:
            node['transport'] = {
                'type':'http'
            }
        if netquery['type'] == 'ws':
            node['transport'] = {
                'type':'ws',
                "path": netquery['path'].rsplit("?")[0],
                "headers": {
                "Host": netquery.get('sni')
                }
            }
        if netquery['type'] == 'grpc':
            node['transport'] = {
                'type':'grpc',
                'service_name':netquery.get('serverName', '')
            }
    return node
