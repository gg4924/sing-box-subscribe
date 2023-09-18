import base64,json
from urllib.parse import quote

def clash2v2ray(share_link):
    link = ''
    if share_link['type'] == 'vmess':
        vmess_info = {
            "v": "2",
            "ps": share_link['name'].encode('utf-8', 'surrogatepass').decode('utf-8'),
            "add": share_link['server'],
            "port": share_link['port'],
            "id": share_link['uuid'],
            "aid": share_link['alterId'],
            "net": share_link['network'],
            "type": "none",
            "host": share_link.get('ws-headers', {}).get('Host', ''),
            "path": share_link.get('ws-path', ''),
            "tls": ""
        }
        vmess_json = json.dumps(vmess_info).encode('utf-8')
        vmess_base64 = base64.b64encode(vmess_json).decode('utf-8')
        link = f"vmess://{vmess_base64}"
        # TODO
    elif share_link['type'] == 'ss':
        ss_info = {
            "cipher": share_link['cipher'],
            "password": share_link['password'],
            "server": share_link['server'],
            "port": share_link['port'],
            "name": quote(share_link['name'], 'utf-8')
        }
        base_link = base64.b64encode("{cipher}:{password}@{server}:{port}".format(**ss_info).encode('utf-8')).decode('utf-8')
        link = "ss://{base_link}#{name}".format(base_link=base_link, **ss_info)
    elif share_link['type'] == 'trojan':
        link = "trojan://{password}@{server}:{port}?allowInsecure={allowInsecure}&peer={sni}sni={sni}{skip_cert_verify}#{name}".format(
        password=share_link['password'],
        server=share_link['server'],
        port=share_link['port'],
        allowInsecure=share_link['allowInsecure'] if share_link.get('allowInsecure') else "0",
        sni=share_link['sni'],
        skip_cert_verify="&skip-cert-verify=1" if share_link.get('skip-cert-verify') else "",
        name=quote(share_link['name'], 'utf-8')
    )
    elif share_link['type'] == 'vless':
        pass
        # TODO
    return link
