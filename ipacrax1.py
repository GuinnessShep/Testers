# Google Play Store - Powerful multi Zero Day Android free IAP proxy exploit (Rooted Version)

import argparse
import http.server
import json
import logging
import os
import requests
import shutil
import socketserver
import subprocess
import threading
import time
import re

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_len = int(self.headers.get('Content-Length'))
        content = self.rfile.read(content_len).decode('utf-8')
        package_name = extract_package_name(content)
        product_id = extract_product_id(content)
        token = extract_purchase_token(content)
        purchase_time = int(time.time() * 1000)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes('{"orderId": "' + self.path[1:] + '", "packageName": "' + package_name + '", "productId": "' + product_id + '", "purchaseTime": ' + str(purchase_time) + ', "purchaseState": 0, "purchaseToken": "' + token + '"}', 'utf-8'))

def extract_package_name(content):
    pattern = r'"packageName":"(.+?)"'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    else:
        return args.package

def extract_product_id(content):
    pattern = r'"productId":"(.+?)"'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    else:
        return args.product

def extract_purchase_token(content):
    pattern = r'"purchaseToken":"(.+?)"'
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    else:
        return args.token

def get_app_details(package_name):
    headers = {'User-Agent': 'Googlebot/2.1 (+http://www.google.com/bot.html)'}
    response = requests.get('https://play.google.com/store/apps/details?id=' + package_name, headers=headers)
    pattern = r'itemprop="name">(.+?)<.+?itemprop="description">(.+?)<'
    match = re.search(pattern, response.text, re.DOTALL)
    if match:
        app_name = match.group(1).strip()
        app_description = match.group(2).strip()
        return app_name, app_description
    else:
        return None, None

def enable_proxy():
    subprocess.call(['su', '-c', 'iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination 127.0.0.1:' + str(args.port)])
    subprocess.call(['su', '-c', 'iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination 127.0.0.1:' + str(args.port)])
    subprocess.call(['su', '-c', 'iptables -t nat -A PREROUTING -p tcp --destination 127.0.0.1 --dport ' + str(args.port) + ' -j REDIRECT --to-port 8080'])

def disable_proxy():
    subprocess.call(['su', '-c', 'iptables -t nat -D OUTPUT -p tcp --dport 80 -j DNAT --to-destination 127.0.0.1:' + str(args.port)])
    subprocess.call(['su', '-c', 'iptables -t nat -D OUTPUT -p tcp --dport 443 -j DNAT --to-destination 127.0.0.1:' + str(args.port)])
    subprocess.call(['su', '-c', 'iptables -t nat -D PREROUTING -p tcp --destination 127.0.0.1 --dport ' + str(args.port) + ' -j REDIRECT --to-port 8080'])

def server():
    httpd = socketserver.TCPServer(('', args.port), RequestHandler)
    httpd.serve_forever()

def buy():
    headers = {'Authorization': 'Bearer ' + args.token}
    params = {'packageName': args.package, 'productId': args.product, 'token': args.token}
    response = requests.post('https://android.clients.google.com/vending/api/ApiRequest', headers=headers, data=params)
    data = json.loads(response.content.decode('utf-8'))
    for purchase in data['payload']:
        if purchase['productId'] == args.product and purchase['purchaseState'] == 0:
            print('Purchase successful!')
            return
    print('Purchase failed.')

def exploit():
    app_name, app_description = get_app_details(args.package)
    print('Detected app: ' + app_name)
    print('App description: ' + app_description)
    url = 'http://127.0.0.1:' + str(args.port) + '/' + args.order_id
    headers = {'User-Agent': 'Android-Finsky/8.1.30-80453000 (api=3,versionCode=80843500,sdk=21,device=' + args.device + ',hardware=' + args.hardware + ',product=' + args.product + ')'}
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print('Exploit successful!')
    else:
        print('Exploit failed.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Powerful multi Zero Day Android free IAP proxy exploit (Rooted Version)')
    parser.add_argument('order_id', type=str, help='the order id of the in-app purchase')
    parser.add_argument('--package', type=str, default='com.example.app', help='the package name of the app')
    parser.add_argument('--product', type=str, default='product_id', help='the product id of the in-app purchase')
    parser.add_argument('--token', type=str, default='purchase_token', help='the purchase token of the in-app purchase')
    parser.add_argument('--port', type=int, default=8000, help='the port to listen on')
    parser.add_argument('--device', type=str, default='Android', help='the device name')
    parser.add_argument('--hardware', type=str, default='hammerhead', help='the hardware name')
    args = parser.parse_args()

    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('requests').setLevel(logging.CRITICAL)

    enable_proxy()

    t = threading.Thread(target=server)
    t.daemon = True
    t.start()

    time.sleep(1)

    buy()
    exploit()

    disable_proxy()
