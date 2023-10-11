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
        'private_key': netquery.get('privateKey'),
        'peer_public_key': netquery.get('publicKey'),
        'reserved': [int(_reserved[0]),int(_reserved[1]),int(_reserved[2])]
    }
    ip_value = netquery.get('ip')
    if ',' in ip_value:
        ipv4_value = ip_value.split(",", 1)[0]+"/32"
        ipv6_value = ip_value.split(",", 1)[1]+"/128"
        node['local_address'] = [ipv4_value] + [ipv6_value]
    else:
        ipv4_value = ip_value+"/32"
        node['local_address'] = [ipv4_value]
    if netquery.get('presharedKey'):
        node['pre_shared_key'] = netquery['presharedKey']
    return (node)
