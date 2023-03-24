# sing-box-subscribe
根据配置模板生成 sing-box 使用的 config.json，主要用于将机场订阅节点添加到 config，对使用 clash_mode 的配置才有意义。
不适合完全不了解 sing-box 配置文件的人使用，最少要知道什么是出站、dns server、dns规则、路由规则。最好了解 clash 的分组方式。

请查看：[https://sing-box.sagernet.org/zh/configuration](https://sing-box.sagernet.org/zh/configuration)。

不支持转换 clash 配置订阅，暂时只写了 vmess、trojan、ss、ssr 协议的分享链接的解析，因为自己用的机场只有这几个协议，vless等其他没有。添加新的协议解析有能力可以自己写，比如 vless.py（文件名称必须为协议名称），写好后将其放入到 parsers 目录即可，vless.py 中必须包含 parse 函数。

**脚本为自用，本人使用 [yacd](https://github.com/haishanh/yacd) 进行节点切换管理（类型为urltest、selector的出站），配合规则像clash一样分流，非常方便。需求跟我一样的可以尝试，但使用脚本过程中有新的功能需求或者出现任何错误请自行解决**。
# 环境
需要安装最新版本 python，并安装下面的依赖：
```
pip install requests paramiko scp
```
使用下面的命令运行脚本：
```
python main.py
```
windows系统建议将命令添加到批处理程序运行。

使用前先编辑 providers.json 文件以及 config_template 目录下的 json 模板文件。
# providers.json文件
在这个文件中添加订阅链接，以及基础设置。
```json
{
    "subscribes":[
        {
            "url": "订阅地址1",
            "tag": "名称2"
        },
        {
            "url": "订阅地址2",
            "tag": "名称2"
            
        }
    ],
    "node_server_dns":"nodedns",
    "auto_set_outbounds_dns":"remote_cf",
    "save_config_path": "D:/Tools/sing-box/profile/config.json",
    "exlude_protocol":"ssr"
}
```
订阅 url 支持设置机场订阅链接以及本地文件路径。本地文件比如txt文件，需要在文件中每行一个添加单节点分享链接，比如ss://abcdefg（非订阅链接）。

订阅 tag 会使用在 config模板文件 中，具体使用方法可以查看下方的 config模板 部分。节点名称也会添加 [订阅tag] 前缀，比如 [订阅tag]美国节点1。

node_server_dns：必需。
  - 将其设置为 config 模板文件中存在的一个 dns server 的 tag，此 dns server 的 detour 必须为direct。
  - 脚本会将所有订阅中的节点服务器域名地址添加到 config 中的 dns 规则中，使用此 dns server 进行解析，避免解析死循环。

auto_set_outbounds_dns：非必需。
  - 将其设置为 config 模板文件中存在的一个 dns server 的 tag，dns server 建议为国外提供的 doh、dot 等服务。
  - 此设置主要为解决 路由出站 和 dns 出站 不一致的问题，比如访问 netflix.com，路由出站为新加坡节点 a ，但使用的 dns server 出站可能为美国节点 b。
  - 设置此项后，脚本会将 路由规则 自动适配到 dns 规则，保证其出站一致。
  
 save_config_path：必需。设置生成的配置文件路径。
 
 exlude_protocol：非必需。
  - 设置不解析的协议，多个使用英文逗号分隔，比如ssr,vmess。
  - 使用此设置中的协议的分享链接会被忽略。
  - sing-box release中的程序没有支持ssr（需要自己添加参数构建），所以此设置可能有用。
# config模板文件
脚本会在 config_template 目录下查找 json 模板文件，脚本运行时可以选择使用的模板文件。

比如目录下存在 tun.json 和 socks.json 两个模板文件。

![Snipaste_2023-03-24_22-16-49](https://user-images.githubusercontent.com/21310130/227548643-ffbf3825-9304-4df7-9b65-82a935227aef.png)

脚本不会检查模板文件的正确性，模板文件不正确会出现错误并无法运行脚本。

目录下自带有一个模板，根据需要修改（必须修改）。
```json
{
  "dns": {
    "servers": [
      {
        "tag": "remote_gg",
        "address": "tls://dns.google",
        "address_resolver": "local",
        "address_strategy": "prefer_ipv4",
        "strategy": "prefer_ipv4"
      },
      {
        "tag": "remote_cf",
        "address": "https://1.0.0.1/dns-query",
        "strategy": "prefer_ipv4"
      },
      {
        "tag": "nodedns",
        "address": "https://doh.pub/dns-query",
        "address_resolver": "local",
        "address_strategy": "prefer_ipv4",
        "strategy": "prefer_ipv4",
        "detour": "direct"
      },
      {
        "tag": "local",
        "address": "建议设置为本地上游路由器地址",
        "detour": "direct"
      },
      {
        "tag": "block",
        "address": "rcode://success"
      }
    ],
    "rules": [
      {
        "geosite": "cn",
        "domain_suffix": [
          "msftconnecttest.com"
        ],
        "server": "local"
      },
      {
        "clash_mode": "direct",
        "server": "local"
      }
    ],
    "strategy": "prefer_ipv4"
  },
  "inbounds": [
    {
      "type": "tun",
      "inet4_address": "172.19.0.1/30",
      "auto_route": true,
      "strict_route": false,
      "sniff": true
    }
  ],
  "outbounds": [
    {
      "tag":"proxy",
      "type":"selector",
      "outbounds":[
        "auto",
        "{all}"
      ]
    },
    {
      "tag":"netflix",
      "type":"selector",
      "outbounds":[
        "{机场 1 tag}",
        "{机场 2 tag}"
      ],
      "filter":[
        {"action":"include","keywords":["sg","新加坡","tw","台湾"]},
        {"action":"exlude","keywords":["ˣ²"],"for":["机场tag"]}
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
      "type": "block",
      "tag": "block"
    },
    {
      "type": "dns",
      "tag": "dns-out"
    }
  ],
  "route": {
    "rules": [
      {
        "port": 53,
        "outbound": "dns-out"
      },
      {
        "protocol": "dns",
        "outbound": "dns-out"
      },
      {
        "clash_mode": "direct",
        "outbound": "direct"
      },
      {
        "protocol": "quic",
        "outbound": "block"
      },
      {
        "geoip": [
          "private",
          "cn"
        ],
        "outbound": "direct"
      },
      {
        "geosite": "cn",
        "domain_suffix":[
          "msftconnecttest.com",
          "doppiocdn.com",
          "tpkcz.icu",
          "pixeldrain.com"
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
模板文件基本等同于 sing-box config，不过有一些新的参数，比如 {all}、{机场tag}、filter，所有参数仅在clash_mode的出站方式下才会生效，出站类型为 urltest、selector。
```json
{
  "tag":"proxy",
  "type":"selector",
  "outbounds":[
    "auto",
    "{all}"
  ],
  "filter":[
    {"action":"exlude","keywords":["ˣ²"],"for":["机场tag"]}
  ]
},
{
  "tag":"netflix",
  "type":"selector",
  "outbounds":[
    "{机场 1 tag}",
    "{机场 2 tag}"
  ],
  "filter":[
    {"action":"include","keywords":["sg","新加坡","tw","台湾"]},
    {"action":"exlude","keywords":["ˣ²"],"for":["机场tag"]}
  ]
}
```
- {all}：表示所有订阅中的所有节点。脚本会将所有节点添加到有此标识的 outbounds 中。

- {机场tag}：在 providers.json 中设置的机场 tag 可以用于此处，代表此订阅中的所有节点。

- filter：非必需。节点过滤，为一个数组对象，可以添加任意条规则，格式为:
```json
"filter":[
    {"action":"include","keywords":["保留关键字1","保留关键字2"]},
    {"action":"exlude","keywords":["排除关键字1","保留关键字2"],"for":["机场tag"]}
  ]
```
- include：后面添加要保留的关键字，名称中包含这些关键字的节点都将被保留，其他节点会被删除。

- exlude：后面添加要排除的关键字，名称中包含这些关键字的节点都将被删除，其他节点会被保留。

- for：非必需。设置机场tag，可以多个，表示此规则只对指定的机场起作用，其他机场会忽略这个规则。

多个规则会按顺序执行过滤。

<details><summary><b>效果参考</b></summary>

<p>

具体效果根据个人的出站及规则设置决定。
</p>
<p>

![Snipaste_2023-03-24_23-54-45](https://user-images.githubusercontent.com/21310130/227577941-01c80cfc-1cd9-4f95-a709-f5442a2a2058.png)

![Snipaste_2023-03-24_23-55-24](https://user-images.githubusercontent.com/21310130/227577968-6747c7aa-db61-4f6c-b7cc-e3802e34cc3d.png)    
</p>
</details>

# 感谢
- [sing-box](https://github.com/SagerNet/sing-box)
- [yacd](https://github.com/haishanh/yacd)
- [clash](https://github.com/Dreamacro/clash)

部分协议解析参考了[convert2clash](https://github.com/waited33/convert2clash)
