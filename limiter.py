from glob import glob
import os;
import sqlite3;
import time;
import requests;
import subprocess;
import threading;
import schedule;
import re
import json
import urllib.parse


_db_address = '/etc/x-ui/x-ui.db'
_max_allowed_connections = 1
_checkCycle = 60 #seconds
_telegrambot_token = 'YOUR_TELEGRAM_TOKEN_BOT'
_telegram_chat_id = '' # you can get this in @cid_bot bot.
_sv_addr = 'Burstable-1'

def extract_limit(remark, default=_max_allowed_connections):
    match = re.search(r'\[(\d+)\]', remark)
    if match:
        return int(match.group(1))
    return default

def getUsers():
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select id,remark,port,settings from inbounds where id > 0 and enable=1")

    users_list = []
    for row in cursor:
        remark = row[1]
        port = row[2]
        settings_json = row[3]
        limit = extract_limit(remark)
        settings = json.loads(settings_json)
        clients = settings.get("clients", [])
        for client in clients:
            email = client.get("email", "no-email")
            telegram_id = client.get("tgId", "none")
            users_list.append({'name': remark, 'port': port, 'limit': limit, 'email': email, 'telegram_id': telegram_id})

    conn.close();
    return users_list

def disableAccount(user_port):
    conn = sqlite3.connect(_db_address) 
    conn.execute(f"update inbounds set enable = 0 where port={user_port}");
    conn.commit()
    conn.close();
    time.sleep(2)
    os.popen("x-ui restart")
    time.sleep(3)
    
def checkNewUsers():
    conn = sqlite3.connect(_db_address)
    cursor = conn.execute(f"select count(*) from inbounds WHERE id > {_user_last_id}");
    new_counts = cursor.fetchone()[0];
    conn.close();
    if new_counts > 0:
        init()

def fireUP():
    users_list = getUsers();
    for user in users_list:
        checker = AccessChecker(user)
        checker.run()
class AccessChecker():
    def __init__(self, user):
        self.user = user;
    def run(self):
        time.sleep(5)
        print(f"checking {self.user['name']}")
        user_remark = self.user['name'];
        user_port = self.user['port'];
        user_limit = self.user['limit'];
        user_email = self.user['email'];
        user_telegram_id = self.user['telegram_id'];
        message = f"""{user_email} جان :
کانفیگ شما تک کاربره می‌باشد و به دلیل استفاده بیش از حد مجاز، کانفیگ شما از دسترس خارج شد.
لطفاً برای فعال شدن کانفیگ به پشتیبانی پیام بده.
توجه داشته باش قطع شدن بیش از سه بار باعث قطع دائمی کانفیگ خواهد شد."""

        # تبدیل به فرمت مناسب URL
        encoded_message = urllib.parse.quote(message)
        netstate_data =  os.popen("netstat -np 2>/dev/null | grep :"+str(user_port)+" | awk '{if($3!=0) print $5;}' | cut -d: -f1 | sort | uniq -c | sort -nr | head").read();
        netstate_data = str(netstate_data)
        connection_count =  len(netstate_data.split("\n")) - 1;
        log_file = "/root/x-ui-device-limiter/limiter-check.log"

        if connection_count > user_limit:
           with open(log_file, "a") as f:
               f.write(f"\n[{time.ctime()}] {user_remark} (Port {user_port}) (UserLimit {user_limit}) (ConnectionCount {connection_count}) (TGID {user_telegram_id})\n")
           print("c "+str(user_port) + "-"+ str(connection_count)+" - "+str(_max_allowed_connections))
           requests.get(f'https://api.telegram.org/bot{_telegrambot_token}/sendMessage?chat_id={user_telegram_id}&text={encoded_message}\n{_sv_addr}')
           disableAccount(user_port=user_port)
           print(f"inbound with port {user_port} blocked")
while True:
    fireUP()
    time.sleep(_checkCycle)


