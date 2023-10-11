import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    netquery = dict(
        (k, v.replace(' ', '+') if len(v) > 1 else v[0].replace(' ', '+'))
        for k, v in parse_qs(server_info.query).items()
    )
    _reserved = netquery.get('reserved').split(",")
    node = {
        'tag': unquote(server_info.fragment) or tool.genName()+'_wireguard',
        'type': 'wireguard',
        'server': re.sub(r"\[|\]", "", server_info.netloc.rsplit(":", 1)[0]),
        'server_port': int(server_info.netloc.rsplit(":", 1)[1]),
        'local_address': [
            netquery.get('ip').split(",", 1)[0]+"/32"
        ],
        'private_key': netquery.get('privateKey'),
        'peer_public_key': netquery.get('publicKey'),
        'reserved': [int(_reserved[0]),int(_reserved[1]),int(_reserved[2])]
    }
    if netquery.get('ip').split(",", 1)[1]:
        node['local_address'].append(netquery.get('ip').split(",", 1)[1]+"/128")
    if netquery.get('presharedKey'):
        node['pre_shared_key'] = netquery['presharedKey']
    return (node)
