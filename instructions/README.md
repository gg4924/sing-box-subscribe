# sing-box-subscribe

Generate the `config.json` used by sing-box based on the configuration template. This is mainly used to add subscription nodes to the config for those using the `clash_mode` configuration.

It is not suitable for people who are completely unfamiliar with the sing-box configuration file. At the very least, you should know about outbound, DNS server, DNS rules, and routing rules. It's best to understand clash's grouping method.

Please refer to: [http://sing-box.sagernet.org/configuration](http://sing-box.sagernet.org/configuration/).

## Catalog

[Operation video](https://github.com/Toperlock/sing-box-subscribe/tree/main/instructions/README.md#-demonstration-video)

[Parameter meaning](https://github.com/Toperlock/sing-box-subscribe/tree/main/instructions#providersjson-file)

[Detailed template explanation](https://github.com/Toperlock/sing-box-subscribe/tree/main/instructions#config-template-files)

[Run sing-box on Windows](https://github.com/Toperlock/sing-box-subscribe/tree/main/instructions#windows-sing-box-usage)

## Supported Protocols

|  Protocol | V2 Sub | Clash Sub | URI Format |
|  :----  | :----: | :----: | :----: |
| http  | ✅ | ✅ | ✅ |
| socks5  | ✅ | ✅ | ✅ |
| shadowsocks  | ✅ | ✅ | ✅ |
| shadowsocksR  | ✅ | ✅ | ✅ |
| vmess  | ✅ | ✅ | ✅ |
| trojan  | ✅ | ✅ | ✅ |
| vless  | ✅ | ✅ | ✅ |
| tuic  | ✅ | ✅ | ✅ |
| hysteria  | ✅ | ✅ | ✅ |
| hysteria2  | ✅ | ✅ | ✅ |
| wireguard  | ✅ | ✅ | ✅ |

~Parsing of clash subscriptions is not supported~ Only parsing of the checked protocol sharing links in( **v2 or clash subscription format**) has been implemented for now. You can write your own protocol parsers, for example, `vless.py` (the filename must match the protocol name), and place it in the `parsers` directory. The `vless.py` file must include a `parse` function.

**This script is for personal use. I use [yacd](https://yacd.metacubex.one) (For ios please use http://yacd.metacubex.one) to manage node switching (outbound types `urltest` and `selector`) and distribute traffic like in clash, which is very convenient. If you have similar needs, you can try it, but if you encounter new feature requirements or any errors while using the script, please resolve them on your own**.

**Scripts can be deployed to run on a web page using a vercel server, or you can download the project source code and run it locally. Please use your own deployed website to generate the sing-box configuration.**

# I. Server deployment

## Getting Started

1. Click the fork button on the top right corner of this project to fork this project to your own repository;
2. Click the button on the right to start deployment:
   [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new), and log in directly with your Github account; [Please see the detailed tutorial](../docs/vercel-en.md#how-to-create-a-new-project).
3. Once deployed, you can start using it;
4. (Optional) [Bind a custom domain name](https://vercel.com/docs/concepts/projects/domains/add-a-domain): Vercel's assigned domain DNS is polluted in some zones, bind a custom domain name to connect directly.

### Turn on automatic updates

> If you encounter an Upstream Sync execution error, please manually click Sync Fork once!

After you have forked the project, due to Github's limitations, you need to manually go to the Actions page of the project you have forked to enable Workflows and enable Upstream Sync Action, which will turn on the hourly auto-updates:

![AutoUpdate](https://github.com/Toperlock/ChatGPT-Next-Web/raw/main/docs/images/enable-actions.jpg)

![Enable Automatic Updates](https://github.com/Toperlock/ChatGPT-Next-Web/raw/main/docs/images/enable-actions-sync.jpg)

### Manual update code

If you want to enable manual updates right away, check out [Github's documentation](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/syncing-a-fork) for information on how to synchronize a forked project with your upstream code.

You can star/watch the project or follow the author to be notified of new features.

## Steps for page manipulation

[Sample website](https://sing-box-subscribe.vercel.app/). Open your deployed website, edit the contents of the `编辑服务器 TEMP_JSON_DATA` box on the right side, click `保存`, select the configuration template in the upper left corner, and click `生成配置文件`. 👉🏻[Parameter Fill View](https://github.com/Toperlock/sing-box-subscribe/tree/main/instructions#providersjson-file)

ios with the shortcut command to copy the content of the web page, or too much content to choose to download the file to solve the problem of the file suffix by yourself. 👉🏻[Shortcut Install](https://www.icloud.com/shortcuts/75fd371e0aa8438a89f715238a21ee68)

Android use chrome browser to open the webpage to generate the configuration file, long press the content, select it in full, share it to the code editor, check whether the editor shows the content is complete. 👉🏻[Editor Install](https://mt2.cn/download/)

**Note that after clicking Save, go to Generate Configuration File as soon as possible, otherwise the content you fill in will remain on the webpage, and other people can browse to it when they open the website. Can't think of a solution at the moment**

<div align="left">
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/c3c39033-079e-497c-86ef-532337d0262b" alt="how-to-use" width="70%" />
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/86334052-29ad-4677-bb65-b24bcc01030e" alt="fill-in" width="70%" />
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/60b89287-8b4d-4032-b876-a8eed37de171" alt="result" width="70%" />
</div>

## 🎬 Demonstration video

<div align="center">
      
https://github.com/Toperlock/sing-box-subscribe/assets/86833913/0d106dc0-e845-46e4-b1a8-a655109628e9

</div>

# II. Local installation
### Install [Python](https://www.python.org/) version 3.10 or above on your PC. Make sure to add Python to your system environment variables (follow Google's installation steps).

<div align="left">
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/f387322b-a602-40df-b3b6-95561329f2f8" alt="install" width="60%" />
</div>

### In the terminal, input the following command to install dependencies (on Mac, replace `pip` with `pip3`):

```
pip install requests paramiko scp Flask PyYAML ruamel.yaml
```

<div align="left">
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/0fc03b49-4c57-4ef3-a4fc-044c1a108d75" alt="install" width="60%" />
</div>

### Download the `sing-box-subscribe` project and open the terminal to navigate to the project directory (you can directly type `cmd` in the file path).

<div align="left">
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/73f05ba8-105c-4f10-8e6c-16e27f26c084" alt="run" width="60%" />
</div>

### Put your subscription links in `providers.json`, edit `config_template_groups_tun.json` file and use the following command to run the script after editing the template:

```
python main.py
```

### If you receive module-related errors while using the script, install the corresponding modules using the command provided below (on Mac, replace `pip` with `pip3`):

```
pip install chardet
```
<div align="left">
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/1762db84-23f5-4cbd-a9d1-df3ca253396c" alt="install" width="60%" />
</div>

For Windows systems, it's recommended to add the commands to a batch program for execution.

Before using, make sure to edit the `providers.json` file and the `.json` template files in the `config_template` directory.

A lazy configuration `config_template_groups_tun` file is included, which allows filtering nodes based on different categories:
* Implement `Openai` routing rules
* Implement `Google` routing rules
* Implement `Telegram` routing rules
* Implement `Twitter` routing rules
* Implement `Facebook` routing rules
* Implement `Amazon` routing rules
* Implement `Apple` routing rules
* Implement `Microsoft` routing rules
* Implement `Game` routing rules
* Implement `Bilibili` routing rules
* Implement `Youtube` routing rules
* Implement `Netflix` routing rules
* Implement `Hbo` routing rules
* Implement `Disney` routing rules
* Implement `Prime Video` routing rules

# providers.json File
In this file, you can add subscription links and basic settings.
```json
{
    "subscribes":[
        {
            "url": "subscribe1_link",
            "tag": "airport1_tag",
            "enabled": true,
            "emoji": 1,
            "prefix": ""
        },
        {
            "url": "subscribe2_link",
            "tag": "airport2_tag",
            "enabled": false,
            "emoji": 0,
            "prefix": "❤️node_name prefix - "
        }
    ],
    "auto_set_outbounds_dns":{
        "proxy": "",
        "direct": ""
    },
    "save_config_path": "./config.json",
    "auto_backup": false,
    "exlude_protocol":""
}
```
- `url`: Required.

> Supports setting up a regular V2 subscription link (**content in base64 encoding**)

> Supports setting up a clash subscription link

> Supports setting up a local file paths (**content as URI links**)

    For local files, such as txt files, each line should contain a single node sharing link, starting with `ss://` (non-subscription link).

    Local files need to be saved on the same drive. Local path formats: `/Desktop/sing-box-subscribe/xx.txt` or relative path formats in the same folder as `main.py`: `./xx.txt`.

- `tag`: Required.

> Fill in this tag in the config template to add this subscription. The "airport1_tag" here corresponds to "{机场1}" in the config template. Specific usage can be found in the config template section below.

<details>
      <summary>tag screenshot reference</summary>
  
<div align="left">
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/b8673073-7160-429f-9ced-3eae7925036e" alt="download" width="65%" />
</div>

</details>

- `enabled`: Optional. **Set it to false, and the subscription will be ignored**.

- `emoji`: Optional. **Set it to false or 0, and the node name will not have a country flag emoji**.

- `prefix`: Optional. Set a custom prefix that will be added to the beginning of the node names. If not set, no prefix will be added.

<details>
      <summary>prefix effect reference</summary>
  
![Snipaste_2023-05-02_12-53-27](https://user-images.githubusercontent.com/21310130/235582317-6bb3d0a6-916f-445f-999b-f17b3db41eea.png)

</details>

- `auto_set_outbounds_dns`: Optional.
> Includes `proxy` and `direct` settings.

> `proxy` and `direct` should be set to the `tag` of the `dns server` in the config template file.

> With this option set, the script will automatically adapt routing rules to DNS rules.

> DNS servers for outbound rules with `direct` setting in the routing rules will be set to the specified `direct` outbound.

> Outbound rules that need to be proxied in the routing rules will be set to the corresponding `proxy` outbound, and the script will automatically create a corresponding `dns server` for the proxy outbound, using the `dns server` specified in the `proxy` setting.

- `save_config_path`: Required. Set the path for the generated configuration file.

- `auto_backup`: Optional.
> When set to true, the script will rename the currently used sing-box configuration file to `original_filename.current_time.bak` for backup purposes, in case an incorrect configuration file is generated and needs to be restored.

- `exlude_protocol`: Optional.
> Set the protocols to exclude, separated by commas, e.g., ssr, vmess.

> Sharing links using protocols in this setting will be ignored.

> ~~The sing-box release program does not support ssr (needs additional parameters to build), so this setting might be useful.~~

# config Template Files
The script will search for JSON template files in the `config_template` directory, and you can select which template file to use when the script runs.

For example, if there are `tun.json` and `socks.json` template files in the directory.

![Snipaste_2023-03-24_22-16-49](https://user-images.githubusercontent.com/21310130/227548643-ffbf3825-9304-4df7-9b65-82a935227aef.png)

The script does not validate the correctness of the template files. If the template file is incorrect, errors will occur, and the script won't run.

A default template is included in the directory, which you can modify according to your needs.
```json
{
  "dns": {
    "servers": [
      {
        "tag": "proxyDns",
        "address": "8.8.8.8",
        "detour": "proxy"
      },
      {
        "tag": "localDns",
        "address": "local",
        "detour": "direct"
      },
      {
        "tag": "block",
        "address": "rcode://success"
      },
      {
        "tag": "remote",
        "address": "fakeip"
      }
    ],
    "rules": [
      {
        "geosite": "category-ads-all",
        "server": "block",
        "disable_cache": true
      },
      {
        "outbound": "any",
        "server": "localDns"
      },
      {
        "geosite": [
          "private",
          "cn"
        ],
        "server": "localDns"
      },
      {
        "query_type": [
          "A",
          "AAAA"
        ],
        "server": "remote"
      }
    ],
    "fakeip": {
      "enabled": true,
      "inet4_range": "198.18.0.0/15",
      "inet6_range": "fc00::/18"
    },
    "final": "proxyDns",
    "independent_cache": true,
    "strategy": "ipv4_only"
  },
  "inbounds": [
    {
      "type": "mixed",
      "tag": "mixed-in",
      "listen": "127.0.0.1",
      "listen_port": 7890,
      "sniff": true,
      "sniff_override_destination": false,
      "domain_strategy": "ipv4_only"
    },
    {
      "type": "tun",
      "tag": "tun-in",
      "inet4_address": "172.19.0.1/30",
      "inet6_address": "fdfe:dcba:9876::1/126",
      "mtu": 9000,
      "auto_route": true,
      "strict_route": true,
      "sniff": true,
      "endpoint_independent_nat": false,
      "stack": "system",
      "platform": {
        "http_proxy": {
          "enabled": true,
          "server": "127.0.0.1",
          "server_port": 7890
        }
      }
    }
  ],
  "outbounds": [
    {
      "tag":"proxy",
      "type":"selector",
      "outbounds":[
        "auto",
        "{all}"//All nodes of all subscriptions are added to the location of this tag
      ],
    },
    {
      "tag":"netflix",
      "type":"selector",
      "outbounds":[
        "{机场1}",//Tag with the airport1_tag will be added to this tagged location
        "{机场2}"//Tag with the airport2_tag will be added to this tagged location
      ],
      "filter":[
        //If airport1_tag and airport2_tag have nodes with these names 'sg','新加坡','tw','台湾' they collectively form the netflix group
        {"action":"include","keywords":["sg","新加坡","tw","台湾"]},
        //The "for" is set to airport1_tag, which means that this rule only works on airport1_tag
        {"action":"exlude","keywords":["ˣ²"],"for":["机场1"]}
        //This filter will remove nodes containing ˣ² in airport1_tag
      ]
    },
    {
      "tag":"speedtest",
      "type":"selector",
      "outbounds":[
        "direct",
        "proxy"
      ]
    },
    {
      "tag":"auto",
      "type":"urltest",
      "outbounds":[
        "{all}"
      ],
      "url": "http://www.gstatic.com/generate_204",
      "interval": "1m",
      "tolerance": 50
    },
    {
      "type": "direct",
      "tag": "direct"
    },
    {
      "type": "dns",
      "tag": "dns"
    },
    {
      "type": "block",
      "tag": "block"
    }
  ],
  "route": {
    "rules": [
      {
        "protocol": "dns",
        "outbound": "dns"
      },
      {
        "network": "udp",
        "port": 443,
        "outbound": "block"
      },
      {
        "geosite": "category-ads-all",
        "outbound": "block"
      },
      {
        "geosite": [
          "private",
          "cn"
        ],
        "outbound": "direct"
      },
      {
        "geoip": [
          "private",
          "cn"
        ],
        "outbound": "direct"
      },
      {
        "clash_mode": "direct",
        "outbound": "direct"
      },
      {
        "domain": [
          "clash.razord.top",
          "yacd.haishan.me"
        ],
        "outbound": "direct"
      },
      {
        "domain_keyword":[
          "speedtest"
        ],
        "domain_suffix":[
          "cdnst.net",
          "ziffstatic.com"
        ],
        "outbound": "speedtest"
      },
      {
        "geoip":"netflix",
        "geosite":"netflix",
        "outbound":"netflix"
      }
    ],
    "auto_detect_interface": true
  },
  "experimental": {
    "clash_api": {
      "external_controller": "127.0.0.1:9090",
      "external_ui": "ui",
      "default_mode": "rule",
      "store_selected": true
    }
  }
}
```
The template files are similar to sing-box configs, but with some new parameters like `{all}`, `{机场tag}` (translated as `{airport_tag}`), `filter`, which only work with `clash_mode` in `urltest` and `selector` outbounds.
```json
{
  "tag":"proxy",
  "type":"selector",
  "outbounds":[
    "auto",
    "{all}"//All nodes of all subscriptions are added to the location of this tag
  ],
  "filter":[
    //This filter will remove nodes containing ˣ² in airport1_tag
    {"action":"exlude","keywords":["ˣ²"],"for":["机场1"]}
  ]
},
{
  "tag":"netflix",
  "type":"selector",
  "outbounds":[
    "{机场1}",//Tag with the airport1_tag will be added to this tagged location
    "{机场2}"//Tag with the airport2_tag will be added to this tagged location
  ],
  "filter":[
    //If airport1_tag and airport2_tag have nodes with these names 'sg','新加坡','tw','台湾' they collectively form the netflix group
    {"action":"include","keywords":["sg","新加坡","tw","台湾"]},
    //The "for" is set to airport1_tag, which means that this rule only works on airport1_tag
    {"action":"exlude","keywords":["ˣ²"],"for":["机场1"]}
    //This filter will remove nodes containing ˣ² in airport1_tag
  ]
}
```
- `{all}`: Represents all nodes in all subscriptions. The script will add all nodes to the `outbounds` with this identifier.

- `{机场tag}` (translated as `{airport_tag}`): The airport `tag` set in `providers.json` can be used here, representing all nodes in this subscription.

- `filter`: Optional. Node filtering, an array object where you can add any number of rules, formatted as:
```json
"filter": [
    {"action": "include", "keywords": ["keyword1", "keyword2"]},
    {"action": "exclude", "keywords": ["keyword1", "keyword2"], "for": ["airport1_tag", "airport2_tag"]}
  ]
```
- **Keyword case-sensitive**

- `include`: Add the keywords to be retained. Nodes with names containing these keywords will be retained, and other nodes will be deleted.

- `exclude`: Add the keywords to be excluded. Nodes with names containing these keywords will be deleted, and other nodes will be retained.

- `for`: Optional. Set the airport `tag`, can be multiple. This rule will only apply to the specified airports, and other airports will ignore this rule.

Multiple rules will be executed in order.

# Windows sing-box Usage

1. Download the Windows client program [sing-box-windows-amd64.zip](https://github.com/SagerNet/sing-box/releases).
2. Create a batch file with the content `start /min sing-box.exe run`.
3. Refer to the [client configuration](https://github.com/chika0801/sing-box-examples/blob/main/Tun/config_client_windows.json) example, modify as needed, and change the filename to **config.json**, then put the batch file in the same folder as **sing-box.exe**.
4. Right-click **sing-box.exe**, select Properties, go to Compatibility, and choose to run the program as an administrator.
5. Run the batch file, and in the User Account Control dialog that appears, choose Yes.

<details>
      <summary><b>Effect Reference</b></summary>

The specific effects depend on individual outbound and rule settings.

<div align="left">
  <img src="https://user-images.githubusercontent.com/21310130/227577941-01c80cfc-1cd9-4f95-a709-f5442a2a2058.png" alt="download" width="50%" />
  <img src="https://user-images.githubusercontent.com/21310130/227577968-6747c7aa-db61-4f6c-b7cc-e3802e34cc3d.png" alt="download" width="50%" />
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/955968d7-98e7-4bd2-a582-02576877dba1" alt="download" width="50%" />
  <img src="https://github.com/Toperlock/sing-box-subscribe/assets/86833913/9e7c35ff-c6c4-46c4-a74b-624ff72c17ea" alt="download" width="50%" />
</div>

</details>

# Thanks
- [xream](https://github.com/xream)
- [sing-box](https://github.com/SagerNet/sing-box)
- [yacd](https://github.com/haishanh/yacd)
- [clash](https://github.com/Dreamacro/clash)
- [sing-box-examples@chika0801](https://github.com/chika0801/sing-box-examples)

Some protocol parsing referenced from [convert2clash](https://github.com/waited33/convert2clash).

Some clash2v2ray parsing referenced from [clash2base64](https://github.com/yuanyiwei/toys/blob/master/DEPRECATED/clash/clash2base64.py).

Some synchronization code referenced from [ChatGPT-Next-Web](https://github.com/Yidadaa/ChatGPT-Next-Web).
