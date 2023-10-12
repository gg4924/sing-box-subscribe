import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    try:
        remark = (tool.b64Decode(server_info.netloc)).decode().rsplit("/#", 1)
    except UnicodeDecodeError:
        remark = (tool.b64Decode(server_info.netloc+server_info.path)).decode().rsplit("/#", 1)
    _netloc = remark[0].rsplit("@", 1)
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': unquote(remark[1]) if len(remark) > 1 else tool.genName() + '_http',
        'type': 'http',
        'server': re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0]),
        'server_port': int(_netloc[1].rsplit(":", 1)[1]),
        'username': _netloc[0].split(":")[0],
        'password': _netloc[0].split(":")[1],
        'tls': {
            'enabled': True
        }
    }
    if netquery.get('insecure') and netquery['insecure'] == '1' :
        node['tls']['insecure'] = True
    return (node)
