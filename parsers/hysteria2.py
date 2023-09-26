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
        'type': 'hysteria2',
        'server': re.sub(r"\[|\]", "", server_info.netloc.split("@")[1].rsplit(":", 1)[0]),
        'server_port': int(server_info.netloc.rsplit(":", 1)[1].split(",")[0]),
        'obfs': {
            'type': netquery.get('obfs', ''),
            'password': netquery.get('obfs-password', ''),
        },
        "password": server_info.netloc.split("@")[0].rsplit(":", 1)[-1],
        'tls': {
            'enabled': True,
            'server_name': netquery.get('sni', re.sub(r"\[|\]", "", server_info.netloc.split("@")[1].rsplit(":", 1)[0]))
        }
    }
    node['tls']['alpn'] = [netquery.get('alpn', '').strip('{}').split(',')] if netquery.get('alpn') != '' else ["h3"]
    if netquery.get('upmbps'):
        node['tls']['up_mbps'] = int(netquery.get('upmbps'))
    if netquery.get('downmbps'):
        node['tls']['down_mbps'] = int(netquery.get('downmbps'))
    if netquery.get('insecure') and netquery['insecure'] == '1' or netquery.get('allowInsecure') and netquery['allowInsecure'] == '1':
        node['tls']['insecure'] = True
    return (node)
