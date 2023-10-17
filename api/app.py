from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify, Response
import json
import os
import sys
import subprocess
import argparse  # 添加 argparse 模块
import tempfile
import shutil
import tempfile  # 导入 tempfile 模块
from datetime import datetime, timedelta

app = Flask(__name__, template_folder='../templates')  # 指定模板文件夹的路径
app.secret_key = 'sing-box'  # 替换为实际的密钥
os.environ['TEMP_JSON_DATA'] = '{"subscribes":[{"url":"订阅地址","tag":"机场1","enabled":true,"emoji":1,"prefix":""},{"url":"订阅地址","tag":"机场2","enabled":false,"emoji":0,"prefix":"❤️机场前缀 - "}],"auto_set_outbounds_dns":{"proxy":"","direct":""},"save_config_path":"./config.json","auto_backup":false,"exlude_protocol":"ssr","User-Agent":"clashmeta","Only-nodes":false}'

# 获取系统默认的临时目录路径
TEMP_DIR = tempfile.gettempdir()

"""
# 存储配置文件的过期时间（10分钟）
config_expiry_time = None
"""

def cleanup_temp_config():
    global config_expiry_time, config_file_path
    if config_expiry_time and datetime.now() > config_expiry_time:
        shutil.rmtree(os.path.dirname(config_file_path), ignore_errors=True)
        config_expiry_time = None
        config_file_path = None

# 获取临时 JSON 数据
def get_temp_json_data():
    temp_json_data = os.environ.get('TEMP_JSON_DATA')
    if temp_json_data:
        return json.loads(temp_json_data)
    return {}

# 获取config_template目录下的模板文件列表
def get_template_list():
    template_list = []
    config_template_dir = 'config_template'  # 配置模板文件夹路径
    template_files = os.listdir(config_template_dir)  # 获取文件夹中的所有文件
    template_list = [os.path.splitext(file)[0] for file in template_files if file.endswith('.json')]  # 移除扩展名并过滤出以.json结尾的文件
    template_list.sort()  # 对文件名进行排序
    return template_list

# 读取providers.json文件的内容，如果有临时 JSON 数据则使用它
def read_providers_json():
    temp_json_data = get_temp_json_data()
    if temp_json_data :
        return temp_json_data
    with open('providers.json', 'r', encoding='utf-8') as json_file:
        providers_data = json.load(json_file)
    return providers_data

# 写入providers.json文件的内容，如果有临时 JSON 数据则不写入
def write_providers_json(data):
    temp_json_data = get_temp_json_data()
    if not temp_json_data:
        with open('providers.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)

@app.route('/')
def index():
    template_list = get_template_list()
    template_options = [f"{index + 1}、{template}" for index, template in enumerate(template_list)]
    providers_data = read_providers_json()
    temp_json_data = get_temp_json_data()
    return render_template('index.html', template_options=template_options, providers_data=json.dumps(providers_data, indent=4, ensure_ascii=False), temp_json_data=json.dumps(temp_json_data, indent=4, ensure_ascii=False))

@app.route('/update_providers', methods=['POST'])
def update_providers():
    try:
        # 获取表单提交的数据
        new_providers_data = json.loads(request.form.get('providers_data'))
        # 更新providers.json文件
        write_providers_json(new_providers_data)
        flash('Providers.json文件已更新', 'success')
    except Exception as e:
        flash(f'更新Providers.json文件时出错；{str(e)}', 'error')
    return redirect(url_for('index'))

@app.route('/edit_temp_json', methods=['GET', 'POST'])
def edit_temp_json():
    if request.method == 'POST':
        try:
            new_temp_json_data = request.form.get('temp_json_data')
            print (new_temp_json_data)
            if new_temp_json_data:
                temp_json_data = json.loads(new_temp_json_data)
                os.environ['TEMP_JSON_DATA'] = json.dumps(temp_json_data, indent=4, ensure_ascii=False)
                flash('TEMP_JSON_DATA 已更新', 'success')
                return jsonify({'status': 'success'})  # 返回成功状态
            else:
                flash('TEMP_JSON_DATA 不能为空', 'error')
                return jsonify({'status': 'error', 'message': 'TEMP_JSON_DATA 不能为空'})  # 返回错误状态和消息
        except Exception as e:
            flash(f'更新 TEMP_JSON_DATA 时出错：注意订阅链接末尾不要有换行，要在双引号""里面！！！')
            flash(f'Error updating TEMP_JSON_DATA: note that the subscription link should not have a newline at the end, but should be inside double quotes ""')
            return jsonify({'status': 'error', 'message': str(e)})  # 返回错误状态和消息

@app.route('/generate_config', methods=['POST'])
def generate_config():
    try:
        selected_template_index = request.form.get('template_index')
        if not selected_template_index:
            flash('请选择一个配置模板', 'error')
            return redirect(url_for('index'))
        temp_json_data = json.dumps(os.environ['TEMP_JSON_DATA'], indent=4, ensure_ascii=False)
        # 修改这里：执行main.py并传递模板序号作为命令行参数，如果未指定，则传递空字符串
        subprocess.check_call([sys.executable, 'main.py', '--template_index', selected_template_index, '--temp_json_data', temp_json_data])
        CONFIG_FILE_NAME = json.loads(os.environ['TEMP_JSON_DATA']).get("save_config_path", "config.json")
        if CONFIG_FILE_NAME.startswith("./"):
            CONFIG_FILE_NAME = CONFIG_FILE_NAME[2:]
        # 设置配置文件的完整路径
        config_file_path = os.path.join('/tmp/', CONFIG_FILE_NAME) 
        if not os.path.exists(config_file_path):
            config_file_path = CONFIG_FILE_NAME  # 使用相对于当前工作目录的路径 
        os.environ['TEMP_JSON_DATA'] = json.dumps(json.loads('{"subscribes":[{"url":"订阅地址","tag":"机场1","enabled":true,"emoji":1,"prefix":""},{"url":"订阅地址","tag":"机场2","enabled":false,"emoji":0,"prefix":"❤️机场前缀 - "}],"auto_set_outbounds_dns":{"proxy":"","direct":""},"save_config_path":"./config.json","auto_backup":false,"exlude_protocol":"ssr","User-Agent":"clashmeta","Only-nodes":false}'), indent=4, ensure_ascii=False)
        # 读取配置文件内容
        with open(config_file_path, 'r', encoding='utf-8') as config_file:
            config_content = config_file.read()
            if config_content:
                flash('配置文件生成成功', 'success')
        config_data = json.loads(config_content)
        return Response(config_content, content_type='text/plain; charset=utf-8')
    except subprocess.CalledProcessError as e:
        os.environ['TEMP_JSON_DATA'] = json.dumps(json.loads('{"subscribes":[{"url":"订阅地址","tag":"机场1","enabled":true,"emoji":1,"prefix":""},{"url":"订阅地址","tag":"机场2","enabled":false,"emoji":0,"prefix":"❤️机场前缀 - "}],"auto_set_outbounds_dns":{"proxy":"","direct":""},"save_config_path":"./config.json","auto_backup":false,"exlude_protocol":"ssr","User-Agent":"clashmeta","Only-nodes":false}'), indent=4, ensure_ascii=False)
        flash(f'执行子进程时出错，获取链接内容超时，请尝试本地运行脚本或者把订阅链接内容放到gist')
        flash(f'Fetching the link content is timing out, please try running the script locally or putting the subscription link content into Github Gist')
    except Exception as e:
        flash(f'订阅解析超时: 请检查订阅链接是否正确 or 请更换为no_groups模板 再尝试一次')
        flash(f'请不要修改 tag 值，除非你明白它是干什么的')
        flash(f'Error occurred while generating the configuration file: {str(e)}', 'error')
        flash(f'Subscription parsing timeout: Please check if the subscription link is correct or please change to "no_groups_template" and try again')
        flash(f'Please do not modify the "tag" value unless you understand what it does.')
    return redirect(url_for('index'))

@app.route('/clear_temp_json_data', methods=['POST'])
def clear_temp_json_data():
    try:
        os.environ['TEMP_JSON_DATA'] = json.dumps({}, indent=4, ensure_ascii=False)
        flash('TEMP_JSON_DATA 已清空', 'success')
    except Exception as e:
        flash(f'清空 TEMP_JSON_DATA 时出错：{str(e)}', 'error')
    return jsonify({'status': 'success'})

"""
@app.route('/download_config', methods=['GET'])
def download_config():
    try:
        if config_file_path:
            # 清理临时配置文件
            #cleanup_temp_config()

            # 使用send_file发送文件
            return send_file(config_file_path, as_attachment=True)
        else:
            flash('配置文件不存在或已过期', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        return str(e)  # 或者适当处理异常，例如返回一个错误页面
"""
if __name__ == '__main__':
    app.run(debug=True)
