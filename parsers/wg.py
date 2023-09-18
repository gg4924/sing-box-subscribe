import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    _reserved = netquery.get('reserved').split(",")
    node = {
        'tag': unquote(server_info.fragment),
        'type': 'wireguard',
        'server': re.sub(r"\[|\]", "", server_info.netloc.rsplit(":", 1)[0]),
        'server_port': int(server_info.netloc.rsplit(":", 1)[1]),
        'local_address': [
            netquery.get('ip'),
        ],
        'private_key': netquery.get('privateKey'),
        'peer_public_key': netquery.get('publicKey'),
        'pre_shared_key': netquery.get('presharedKey', ''),
        'reserved': [int(_reserved[0]),int(_reserved[1]),int(_reserved[2])],
        'mtu': int(netquery.get('mtu'))
    }
    if netquery.get('ipv6'):
        node['local_address'].append(netquery.get('ipv6'))
    return (node)
