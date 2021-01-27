#!/usr/bin/env python3

####################################################################
# PANINI APP BOT
#
# Author: Alexander J. Lee
# Description:
# A small solo bot project that helped myself and some friends get limited
# sports cards on paniniamerica.net
#
# github.com/leeaj6
# 
# This is outdated do not attempt to use this to purchase items
# for portfolio purposes only
####################################################################

from PaniniAppBot import *
import threading
import time
import sys


bots = []

num_tasks = 1
qty_per_task = '1'

# Per Task
num_proxies = 0

c_dict = {
    'shipping': {
        'first': 'John',
        'last': 'Smith',
        'street_address_1': '123 Main Street',
        'street_address_2': '',
        'city': 'Beverly Hills',
        'state': 'California',
        'state_code': 'CA',
        'zip_code': '90210'
    },
    'billing': {
        'first': 'John',
        'last': 'Smith',
        'street_address_1': '123 Main Street',
        'street_address_2': '',
        'city': 'Beverly Hills',
        'state': 'California',
        'state_code': 'CA',
        'zip_code': '90210',
        'phone': '8008008888',
        'email': 'fakeemail@email.com',
        'card_type': 'Visa',
        'card_num': '0000000000000000',
        'card_month': '01',
        'card_year': '2019',
        'card_cvn': '000'
    }
}

# Import Proxies
try:
  proxy_list_main = [(line.rstrip('\n').split(":")[2]+":"+line.rstrip('\n').split(":")[3]+"@"+line.rstrip('\n').split(":")[0]+":"+line.rstrip('\n').split(":")[1]) for line in open('proxies.txt')]
except:
  try:
    proxy_list_main = [line.rstrip('\n') for line in open('proxies.txt')]
  except:
    proxy_list_main = []

# Create Tasks / allocate proxies
for i in range(num_tasks):
    proxy_list = []
    try:
        if len(proxy_list_main) <= 0:
            num_proxies = 0
        else:
            if len(proxy_list_main) < num_proxies:
                num_proxies = len(proxy_list_main)
            for p in range(num_proxies):
                proxy_list.append(proxy_list_main[0])
                proxy_list.pop(0)
    except:
        proxy_list=[]
    print('Task {} has {} proxies'.format(i+1, num_proxies))
    #Only touch MASTER_PID if you have one
    #Cat ID: Trading Cards=327, panini instant white sparkle=637, FOTL=482
    bots.append(threading.Thread(target=PaniniAppBot(TASK_NUM=i+1, DELAY=1.0, QTY_PER_TASK=qty_per_task, MASTER_PID='', CATEGORY_ID='482', CHECKOUT_DICT=c_dict, PROXY_LIST=proxy_list).start, args=(), daemon = False))

if __name__ == '__main__':
    try:
        for tr in bots:
           tr.start()
    except Exception as errtxt:
        print (errtxt)
