import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    _netloc = server_info.netloc.split("@")
    #_netloc = (tool.b64Decode(server_info.netloc)).decode().split("@")
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': server_info.fragment,
        'type': 'tuic',
        'server': re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0]),
        'server_port': int(_netloc[1].rsplit(":", 1)[1]),
        'uuid': _netloc[0].split(":")[0],
        'password': _netloc[0].split(":")[1],
        'congestion_control': netquery.get('congestion_control', 'cubic'),
        'udp_relay_mode': netquery.get('udp_relay_mode'),
        'zero_rtt_handshake': False,
        'heartbeat': '10s',
        'tls': {
            'enabled': True,
            'alpn': [netquery.get('alpn')]
        }
    }
    if netquery.get('allow_insecure') and netquery['allow_insecure'] == '1' :
        node['tls']['insecure'] = True
    if netquery['disable_sni'] != '1':
        node['tls']['server_name'] = netquery.get('sni')
    return node
