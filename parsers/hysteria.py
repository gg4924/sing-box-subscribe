import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote

def parse(data):
    info = data[:]
    server_info = urlparse(info)
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': unquote(server_info.fragment),
        'type': 'hysteria',
        'server': re.sub(r"\[|\]", "", server_info.netloc.rsplit(":", 1)[0]),
        'server_port': int(server_info.netloc.rsplit(":", 1)[1]),
        'up_mbps': int(netquery.get('upmbps')),
        'down_mbps': int(netquery.get('downmbps')),
        'auth_str': netquery.get('auth'),
        'tls': {
            'enabled': True,
            'server_name': netquery.get('peer', re.sub(r"\[|\]", "", server_info.netloc.rsplit(":", 1)[0])),
            'alpn': [netquery.get('alpn')]
        }
    }
    if netquery.get('insecure') and netquery['insecure'] == '1' or netquery.get('allowInsecure') and netquery['allowInsecure'] == '1':
        node['tls']['insecure'] = True
    if netquery.get('obfs') and netquery['obfs'] != 'none':
        node['obfs'] = netquery.get('obfs')
    return node
