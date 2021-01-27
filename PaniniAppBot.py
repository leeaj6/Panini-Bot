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

import os
import sys
import requests
import random
import json
import time
from time import sleep
import datetime
import threading
import re
import hashlib
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings()

# Some color escape sequences
underline='\033[04m'
orange='\033[33m'
lightblue='\033[94m'
red='\033[31m'
green='\033[32m'
purple='\033[35m'
lightgrey='\033[37m'
reset='\033[0m'

class PaniniAppBot(object):

  def __init__(self, TASK_NUM, DELAY, QTY_PER_TASK, MASTER_PID, CATEGORY_ID, CHECKOUT_DICT, PROXY_LIST):
    self.session = requests.Session()
    self.session.verify = False

    #User-Agent
    self.APP_UA = "PTPaniniConsumerExp/207 CFNetwork/976 Darwin/18.2.0"
    self.DESKTOP_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"

    # 2Captcha
    self.API_KEY = ""
    self.site_key = ""
    self.proxy = '' # Your proxy for solving
    self.proxies = {'http': 'http://' + self.proxy, 'https': 'https://' + self.proxy}

    # Task
    self.TASK_NUM=TASK_NUM
    self.DELAY = DELAY
    self.QTY_PER_TASK = QTY_PER_TASK

    # Proxies
    self.PROXY_LIST = PROXY_LIST
    self.current_proxy_index = 0
    self.length_of_proxy_list = len(self.PROXY_LIST)

    # IDs
    self.MASTER_PID = MASTER_PID
    self.CATEGORY_ID = CATEGORY_ID
    self.CART_ID=''
    self.PROD_SKU = ''
    self.NAME_SKU = ''
    self.ID_SKU = ''
    self.FULL_SKU = ''

    #SUCCESS
    self.ORDER_NUMBER = "N/A"

    #Shipping Details
    self.shipping_first = CHECKOUT_DICT['shipping']['first']
    self.shipping_last = CHECKOUT_DICT['shipping']['last']
    self.shipping_street_address_1 = CHECKOUT_DICT['shipping']['street_address_1']
    self.shipping_street_address_2 = CHECKOUT_DICT['shipping']['street_address_2']
    self.shipping_city = CHECKOUT_DICT['shipping']['city']
    self.shipping_state = CHECKOUT_DICT['shipping']['state']
    self.shipping_state_code = CHECKOUT_DICT['shipping']['state_code']
    self.shipping_zip_code = CHECKOUT_DICT['shipping']['zip_code']

    #Billing Details
    self.billing_first = CHECKOUT_DICT['billing']['first']
    self.billing_last = CHECKOUT_DICT['billing']['last']
    self.billing_street_address_1 = CHECKOUT_DICT['billing']['street_address_1']
    self.billing_street_address_2 = CHECKOUT_DICT['billing']['street_address_2']
    self.billing_city = CHECKOUT_DICT['billing']['city']
    self.billing_state = CHECKOUT_DICT['billing']['state']
    self.billing_state_code = CHECKOUT_DICT['billing']['state_code']
    self.billing_zip_code = CHECKOUT_DICT['billing']['zip_code']
    self.billing_phone = CHECKOUT_DICT['billing']['phone']
    self.billing_email = CHECKOUT_DICT['billing']['email']
    self.billing_card_type = CHECKOUT_DICT['billing']['card_type']
    self.billing_card_number = CHECKOUT_DICT['billing']['card_num']
    self.billing_card_owner = "{} {}".format(CHECKOUT_DICT['billing']['first'], CHECKOUT_DICT['billing']['last'])
    self.billing_card_month = CHECKOUT_DICT['billing']['card_month']
    self.billing_card_year = CHECKOUT_DICT['billing']['card_year']
    self.billing_card_cvn = CHECKOUT_DICT['billing']['card_cvn']

    self.US_region_codes = {'Alabama': '1', 'Alaska': '2', 'American Samoa': '3', 'Arizona': '4', 'Arkansas': '5', 'Armed Forces Africa': '6', 'Armed Forces Americas': '7', 'Armed Forces Canada': '8', 'Armed Forces Europe': '9', 'Armed Forces Middle East': '10', 'Armed Forces Pacific': '11', 'California': '12', 'Colorado': '13', 'Connecticut': '14', 'Delaware': '15', 'District of Columbia': '16', 'Federated States Of Micronesia': '17', 'Florida': '18', 'Georgia': '19', 'Guam': '20', 'Hawaii': '21', 'Idaho': '22', 'Illinois': '23', 'Indiana': '24', 'Iowa': '25', 'Kansas': '26', 'Kentucky': '27', 'Louisiana': '28', 'Maine': '29', 'Marshall Islands': '30', 'Maryland': '31', 'Massachusetts': '32', 'Michigan': '33', 'Minnesota': '34', 'Mississippi': '35', 'Missouri': '36', 'Montana': '37', 'Nebraska': '38', 'Nevada': '39', 'New Hampshire': '40', 'New Jersey': '41', 'New Mexico': '42', 'New York': '43', 'North Carolina': '44', 'North Dakota': '45', 'Northern Mariana Islands': '46', 'Ohio': '47', 'Oklahoma': '48', 'Oregon': '49', 'Palau': '50', 'Pennsylvania': '51', 'Puerto Rico': '52', 'Rhode Island': '53', 'South Carolina': '54', 'South Dakota': '55', 'Tennessee': '56', 'Texas': '57', 'Utah': '58', 'Vermont': '59', 'Virgin Islands': '60', 'Virginia': '61', 'Washington': '62', 'West Virginia': '63', 'Wisconsin': '64', 'Wyoming': '65'}

  def getCurrentProxy(self):
    if self.current_proxy_index < self.length_of_proxy_list:
      self.current_proxy_index = 0
    return self.proxy_list[self.current_proxy_index]

  def start(self):
    if self.MASTER_PID == '': # Not a specific product
        self.productSearch()
    else:
        self.parseSizeSku()

    self.START_TIME = time.time() # keep track of how long the process took
    self.addToCart()
    self.initializeCheckout()
    self.getShippingMethods()
    self.getPaymentMethods()
    self.placeOrder()
    self.COP_SPEED=f'{time.time() - self.START_TIME} seconds'

  def solveCaptcha(self):
    # 2captcha api solver to handle recaptchas
    try:
      captcha_id = self.session.post("http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}".format(self.API_KEY, self.site_key, "https://www.paniniamerica.net")).text.split('|')[1]
      recaptcha_answer = self.session.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(self.API_KEY, captcha_id)).text
      print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Captcha'.center(50,' ')+reset,lightblue+underline+"Solving.."+reset))
      while 'CAPCHA_NOT_READY' in recaptcha_answer:
        time.sleep(1.5)
        recaptcha_answer = self.session.get("http://2captcha.com/res.php?key={}&action=get&id={}".format(self.API_KEY, captcha_id)).text
      recaptcha_answer = recaptcha_answer.split('|')[1]
      print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Captcha'.center(50,' ')+reset,lightblue+underline+"Solved"+reset))
      print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Captcha'.center(50,' ')+reset,lightblue+underline+(recaptcha_answer)+reset))
      return recaptcha_answer
    except:
      print (str(time.asctime( time.localtime(time.time()) ))+" - Could not solve captcha")
      time.sleep(5)

  def hashSignatureCalc(self,query_data):
    # Create a value for 'Signature' header field
    signature_secret = "@3454XW23739*784298@@*$37ehrej1234*(@&%"
    data_dict = json.loads(query_data)
    query_raw = data_dict['query']
    modified_query = query_raw.replace(' ', '').replace('\n', '').replace('__typename', '')
    unhashed_signature = modified_query+signature_secret+self.CART_ID
    s = hashlib.md5(unhashed_signature.encode())
    return s.hexdigest()

  def productSearch(self):
    # search specified collection for products
    query_data = '{"operationName":"products","variables":{},"query":"query products {\\n  products(attribute_code: [], category_id: '+self.CATEGORY_ID+', current_page: 1, page_size: 20, applied_filters: \\"&searchCriteria[filter_groups][21][filters][0][field]=pan_show_product_in_app_only&searchCriteria[filter_groups][21][filters][0][value]=1&searchCriteria[filter_groups][21][filters][0][condition_type]=neq&searchCriteria[sortOrders][0][field]=created_at&searchCriteria[sortOrders][0][direction]=DESC\\", is_store: true) {\\n    items {\\n      id\\n      name\\n      price\\n      sku\\n      status\\n      image\\n      special_price\\n      reward_points\\n      pan_release_date\\n      special_from_date\\n      special_to_date\\n      pan_offer_start_date\\n      pan_offer_end_date\\n      url_key\\n      qty\\n      final_price\\n      is_in_stock\\n      min_sale_qty\\n      max_sale_qty\\n      type_id\\n      thumbnail\\n      description\\n      short_description\\n      isStore\\n      pan_store_auction_start_price\\n      pan_store_auction_end_price\\n      pan_store_auction_price_drop\\n      isAuction\\n      category_ids\\n      __typename\\n    }\\n    search_criteria {\\n      page_size\\n      current_page\\n      total_count\\n      __typename\\n    }\\n    image\\n    meta_title\\n    meta_keywords\\n    meta_description\\n    short_description\\n    timestamp\\n    __typename\\n  }\\n}\\n"}'

    signature_header=self.hashSignatureCalc(query_data)

    headers = {
        'Origin': 'https://www.paniniamerica.net',
        'x-amz-u-id': '',
        'Authorization': '',
        'content-type': 'application/json',
        'accept': '*/*',
        'User-Agent': self.APP_UA,
        'cart_id': '',
        'Signature': signature_header,
        'Referer': 'https://www.paniniamerica.net/cards.html?s=0&p=1',
        'x-amz-s-id': '',
        'x-amz-cart-id': '',
    }
    prodFound=False
    while not prodFound:
      try:
        # Determine if we are using proxies
        if len(self.PROXY_LIST) > 0:
          self.proxies = {'http': 'http://' + self.getCurrentProxy(), 'https': 'https://' + self.getCurrentProxy()}
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=query_data, proxies=self.proxies)
          self.current_proxy_index+=1
        else:
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=query_data)

        dictionary = json.loads(r.text)
        
        if len(dictionary['data']['products']['items']) > 0: # an item is available
          product_index=dictionary['data']['products']['items'][0]
          self.MASTER_PID = product_index['url_key']
          self.PROD_SKU = product_index['sku']
          self.NAME_SKU = product_index['url_key']
          self.ID_SKU = product_index['id']
          self.PRODUCT_NAME = product_index['name']
          self.FULL_SKU = '{}#$%^{}#$%^{}'.format(self.NAME_SKU, self.PROD_SKU, self.ID_SKU)
          print ('{} | [SKU: {}] [Price: ${}] [Stock: {}]'.format(product_index['name'], self.FULL_SKU, product_index['price'], product_index['qty']))
          prodFound=True
        else:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset, red+'No Products Found'.center(50,' ')+reset,red+underline+str(r.status_code)+reset))
          time.sleep(self.DELAY)
      except Exception as e:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+str(e)+" : Status Code "+str(r.status_code)+reset))
          time.sleep(self.DELAY)

  def parseSizeSku(self):
    # get the sku for a certain product
    query_data = '{"operationName":"item","variables":{},"query":"query item {\\n  item(attribute_code: [], sku: \\"\\", name: \\"'+(self.MASTER_PID)+'\\") {\\n    id\\n    sku\\n    name\\n    price\\n    final_price\\n    description\\n    short_description\\n    category_ids\\n    reward_points\\n    news_from_date\\n    news_to_date\\n    meta_title\\n    meta_keywords\\n    meta_description\\n    qty\\n    min_sale_qty\\n    max_sale_qty\\n    special_price\\n    url_key\\n    is_in_stock\\n    special_from_date\\n    special_to_date\\n    pan_offer_start_date\\n    pan_offer_end_date\\n    isStore\\n    pan_show_qty_left_after\\n    media_gallery_entries {\\n      label\\n      media_type\\n      types\\n      file\\n      __typename\\n    }\\n    type_id\\n    timestamp\\n    tnc\\n    status\\n    options {\\n      attribute_id\\n      attribute_code\\n      label\\n      position\\n      options {\\n        label\\n        value\\n        __typename\\n      }\\n      __typename\\n    }\\n    pan_store_auction_start_price\\n    pan_store_auction_end_price\\n    pan_store_auction_price_drop\\n    isAuction\\n    children {\\n      key\\n      value {\\n        id\\n        sku\\n        name\\n        price\\n        final_price\\n        description\\n        short_description\\n        category_ids\\n        reward_points\\n        news_from_date\\n        news_to_date\\n        meta_title\\n        meta_keywords\\n        meta_description\\n        qty\\n        min_sale_qty\\n        max_sale_qty\\n        special_price\\n        url_key\\n        is_in_stock\\n        special_from_date\\n        special_to_date\\n        pan_offer_start_date\\n        pan_offer_end_date\\n        pan_show_qty_left_after\\n        media_gallery_entries {\\n          label\\n          media_type\\n          types\\n          file\\n          __typename\\n        }\\n        type_id\\n        pan_store_auction_start_price\\n        pan_store_auction_end_price\\n        pan_store_auction_price_drop\\n        isAuction\\n        image\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n"}'

    signature_header=self.hashSignatureCalc(query_data)

    headers = {
        'origin': 'https://www.paniniamerica.net',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': '',
        'signature': signature_header,
        'x-amz-s-id': '',
        'cart_id': '',
        'x-amz-u-id': '',
        'user-agent': self.APP_UA,
        'content-type': 'application/json',
        'accept': '*/*',
        'referer': 'https://www.paniniamerica.net/2018-19-panini-hoops-nba-trading-cards-retail.html%20https://www.paniniamerica.net/2018-19-panini-hoops-nba-trading-cards-retail.html',
        'authority': 'api.paniniamerica.net',
        'x-amz-cart-id': '',
    }

    skuParsed=False
    while not skuParsed:
      try:
        if len(self.PROXY_LIST) > 0:
          self.proxies = {'http': 'http://' + self.getCurrentProxy(), 'https': 'https://' + self.getCurrentProxy()}
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=query_data, proxies=self.proxies)
          self.current_proxy_index+=1
        else:
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=query_data)
        dictionary = json.loads(r.text)
        
        if r.status_code in (200,304):
          self.PROD_SKU = dictionary['data']['item']['sku']
          self.NAME_SKU = dictionary['data']['item']['url_key']
          self.ID_SKU = dictionary['data']['item']['id']
          self.PRODUCT_NAME = dictionary['data']['item']['name']
          self.FULL_SKU = '{}#$%^{}#$%^{}'.format(self.NAME_SKU, self.PROD_SKU, self.ID_SKU)
          print ('{} | [SKU: {}] [Price: ${}] [Stock: {}]'.format(dictionary['data']['item']['name'], self.FULL_SKU, dictionary['data']['item']['price'], dictionary['data']['item']['qty']))
          skuParsed=True
        else:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset, red+'No SKU Matches Found'.center(50,' ')+reset,red+underline+str(r.status_code)+reset))
          time.sleep(self.DELAY)
      except Exception as e:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+str(e)+" : Status Code "+str(r.status_code)+reset))
          time.sleep(self.DELAY)

  def addToCart(self):
    # send a request to add a product, retry if failed (site crashes)
    atc_data = '{"operationName":"cart","variables":{},"query":"query cart {\\n  addToCart(item: {sku: \\"'+(self.PROD_SKU)+'\\", qty: '+self.QTY_PER_TASK+', quote_id: \\"1\\", type: \\"simple\\", info: \\"'+(self.FULL_SKU)+'\\"}) {\\n    sku\\n    message\\n    status\\n    cart_id\\n    qty\\n    __typename\\n  }\\n}\\n"}'

    signature_header=self.hashSignatureCalc(atc_data)

    headers = {
        'origin': 'https://www.paniniamerica.net',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': '',
        'signature': signature_header,
        'x-amz-s-id': '',
        'cart_id': '',
        'x-amz-u-id': '',
        'user-agent': self.APP_UA,
        'content-type': 'application/json',
        'accept': '*/*',
        'referer': 'https://www.paniniamerica.net/2018-19-panini-hoops-nba-trading-cards-retail.html%20https://www.paniniamerica.net/2018-19-panini-hoops-nba-trading-cards-retail.html',
        'authority': 'api.paniniamerica.net',
        'x-amz-cart-id': '',
    }

    added=False
    while not added:
      try:
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=atc_data)
          dictionary = json.loads(r.text)
          if dictionary['data']['addToCart']['message'] == 'Success':
            #print(json.dumps(dictionary,indent=4))
            self.CART_ID = dictionary['data']['addToCart']['cart_id']
            print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Item Added'.center(50,' ')+reset,lightblue+underline+('CART_ID='+self.CART_ID)+reset))
            added=True
          else:
            print(json.dumps(dictionary,indent=4))
            time.sleep(self.DELAY)
      except Exception as e:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+str(e)+" : Status Code "+str(r.status_code)+reset))
          print (r.text)
          time.sleep(self.DELAY)

  def initializeCheckout(self):
    # Begin the Checkout process
    data = '{"operationName":"item","variables":{},"query":"query item {\\n  buynow(item: {sku: \\"\\", qty: 1, quote_id: \\"1\\"}, isNormalBuyFlow: true) {\\n    status\\n    cart_id\\n    session_id\\n    qty\\n    message\\n    __typename\\n  }\\n}\\n"}'

    signature_header=self.hashSignatureCalc(data)

    headers = {
        'origin': 'https://www.paniniamerica.net',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'authorization': '',
        'signature': signature_header,
        'x-amz-s-id': '',
        'cart_id': self.CART_ID,
        'x-amz-u-id': '',
        'user-agent': self.APP_UA,
        'content-type': 'application/json',
        'accept': '*/*',
        'referer': 'https://www.paniniamerica.net/cart.html',
        'authority': 'api.paniniamerica.net',
        'x-amz-cart-id': self.CART_ID,
    }

    started=False
    while not started:
      try:
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=data)
          dictionary = json.loads(r.text)
          if dictionary['data']['buynow']['message'] == 'Success':
            #print(json.dumps(dictionary,indent=4))
            self.SESSION_ID = dictionary['data']['buynow']['session_id']
            print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Checkout Started'.center(50,' ')+reset,lightblue+underline+('SESSION_ID='+self.SESSION_ID)+reset))
            started=True
          else:
            print(dictionary['data']['buynow']['message'])
            time.sleep(self.DELAY)
      except Exception as e:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+str(e)+" : Status Code "+str(r.status_code)+reset))
          print (r.text)
          time.sleep(self.DELAY)

  def getShippingMethods(self):
    # Find the cheapest shipping method
    data = '{"operationName":"getShippingMethods","variables":{},"query":"query getShippingMethods {\\n  getShippingMethods(address: {region: \\"'+(self.shipping_state)+'\\", region_id: '+(self.US_region_codes[self.shipping_state])+', region_code: \\"'+(self.shipping_state_code)+'\\", country_id: \\"US\\", street: [\\"'+(self.shipping_street_address_1)+'\\", \\"'+(self.shipping_street_address_2)+'\\"], postcode: \\"'+(self.shipping_zip_code)+'\\", city: \\"'+(self.shipping_city)+'\\", firstname: \\"'+(self.shipping_first)+'\\", lastname: \\"'+(self.shipping_last)+'\\", customer_id: 0, email: \\"'+(self.billing_email)+'\\", telephone: \\"'+(self.billing_phone)+'\\", save_in_address_book: 0}) {\\n    carrier_code\\n    method_code\\n    carrier_title\\n    method_title\\n    amount\\n    base_amount\\n    available\\n    error_message\\n    price_excl_tax\\n    price_incl_tax\\n    __typename\\n  }\\n}\\n"}'

    signature_header=self.hashSignatureCalc(data)

    headers = {
        'Origin': 'https://www.paniniamerica.net',
        'x-amz-u-id': '',
        'Authorization': '',
        'content-type': 'application/json',
        'accept': '*/*',
        'User-Agent': self.APP_UA,
        'cart_id': self.CART_ID,
        'Signature': signature_header,
        'Referer': 'https://www.paniniamerica.net/cart.html?s=2',
        'x-amz-s-id': self.SESSION_ID,
        'x-amz-cart-id': self.CART_ID,
    }

    started=False
    while not started:
      try:
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=data)
          dictionary = json.loads(r.text)
          if len(dictionary['data']['getShippingMethods']):
            #print(json.dumps(dictionary,indent=4))
            self.SHIPPING_METHOD = dictionary['data']['getShippingMethods'][0]
            print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Cheapest Shipping Method'.center(50,' ')+reset,lightblue+underline+str(self.SHIPPING_METHOD)+reset))
            started=True
          else:
            print(json.dumps(dictionary,indent=4))
            time.sleep(self.DELAY)
      except Exception as e:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+str(e)+" : Status Code "+str(r.status_code)+reset))
          print (r.text)
          time.sleep(self.DELAY)

  def getPaymentMethods(self):
    # Submit billing
    data = '{"operationName":"getPaymentdMethods","variables":{},"query":"query getPaymentdMethods {\\n  getPaymentdMethods(addressInformation: {shipping_carrier_code: \\"'+(self.SHIPPING_METHOD["carrier_code"])+'\\", shipping_method_code: \\"'+(self.SHIPPING_METHOD["method_code"])+'\\", shipping_address: {firstname: \\"'+(self.shipping_first)+'\\", lastname: \\"'+(self.shipping_last)+'\\", email: \\"'+(self.billing_email)+'\\", street: [\\"'+(self.shipping_street_address_1)+'\\", \\"'+(self.shipping_street_address_2)+'\\"], city: \\"'+(self.shipping_city)+'\\", region_id: '+(self.US_region_codes[self.shipping_state])+', region: \\"'+(self.shipping_state)+'\\", region_code: \\"'+(self.shipping_state_code)+'\\", postcode: \\"'+(self.shipping_zip_code)+'\\", country_id: \\"US\\", telephone: \\"'+(self.billing_phone)+'\\", saveInAddressBook: 0}, billing_address: {firstname: \\"'+(self.billing_first)+'\\", lastname: \\"'+(self.billing_last)+'\\", email: \\"'+(self.billing_email)+'\\", street: [\\"'+(self.billing_street_address_1)+'\\", \\"'+(self.billing_street_address_2)+'\\"], city: \\"'+(self.billing_city)+'\\", region_id: '+(self.US_region_codes[self.billing_state])+', region: \\"'+(self.billing_state)+'\\", region_code: \\"'+(self.billing_state_code)+'\\", postcode: \\"'+(self.billing_zip_code)+'\\", country_id: \\"US\\", telephone: \\"'+(self.billing_phone)+'\\"}}) {\\n    payment_methods {\\n      code\\n      title\\n      __typename\\n    }\\n    totals {\\n      grand_total\\n      base_grand_total\\n      subtotal\\n      base_subtotal\\n      discount_amount\\n      base_discount_amount\\n      subtotal_with_discount\\n      base_subtotal_with_discount\\n      shipping_amount\\n      base_shipping_amount\\n      shipping_discount_amount\\n      base_shipping_discount_amount\\n      tax_amount\\n      base_tax_amount\\n      weee_tax_applied_amount\\n      shipping_tax_amount\\n      base_shipping_tax_amount\\n      subtotal_incl_tax\\n      shipping_incl_tax\\n      base_shipping_incl_tax\\n      base_currency_code\\n      quote_currency_code\\n      coupon_code\\n      items_qty\\n      items {\\n        item_id\\n        price\\n        base_price\\n        qty\\n        row_total\\n        base_row_total\\n        row_total_with_discount\\n        tax_amount\\n        base_tax_amount\\n        tax_percent\\n        discount_amount\\n        base_discount_amount\\n        discount_percent\\n        price_incl_tax\\n        base_price_incl_tax\\n        row_total_incl_tax\\n        base_row_total_incl_tax\\n        options\\n        weee_tax_applied_amount\\n        weee_tax_applied\\n        name\\n        __typename\\n      }\\n      total_segments {\\n        code\\n        title\\n        value\\n        __typename\\n      }\\n      __typename\\n    }\\n    message\\n    __typename\\n  }\\n}\\n"}'

    signature_header=self.hashSignatureCalc(data)

    headers = {
        'Origin': 'https://www.paniniamerica.net',
        'x-amz-u-id': '',
        'Authorization': '',
        'content-type': 'application/json',
        'accept': '*/*',
        'User-Agent': self.APP_UA,
        'cart_id': self.CART_ID,
        'Signature': signature_header,
        'Referer': 'https://www.paniniamerica.net/cart.html?s=2',
        'x-amz-s-id': self.SESSION_ID,
        'x-amz-cart-id': self.CART_ID,
    }

    started=False
    while not started:
      try:
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=data)
          dictionary = json.loads(r.text)
          print('This is for debugging:', dictionary['data']['getPaymentdMethods']['totals']['total_segments'])
          shipping_info =  dictionary['data']['getPaymentdMethods']['totals']['total_segments'][1]['title']
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Shipping Method Set is'.center(50,' ')+reset,lightblue+underline+str(shipping_info)+reset))
          if shipping_info not in ['', None] and len(dictionary['data']['getPaymentdMethods']['payment_methods']):
            print(json.dumps(dictionary,indent=4))
            self.PAYMENT_METHOD = dictionary['data']['getPaymentdMethods']['payment_methods'][0]
            print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Payment Method'.center(50,' ')+reset,lightblue+underline+str(self.PAYMENT_METHOD)+reset))
            started=True
          else:
            print(json.dumps(dictionary,indent=4))
            time.sleep(self.DELAY)
      except Exception as e:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+str(e)+" : Status Code "+str(r.status_code)+reset))
          print (r.text)
          time.sleep(self.DELAY)

  def placeOrder(self):
    # complete order for the current cart
    started=False
    while not started:
      try:
          data = '{"operationName":"placeOrder","variables":{},"query":"query placeOrder {\\n  guestPlaceOrder(cartId: \\"'+(self.CART_ID)+'\\", billingAddress: {countryId: \\"US\\", regionId: \\"'+(self.US_region_codes[self.billing_state])+'\\", regionCode: \\"'+(self.billing_state_code)+'\\", region: \\"'+(self.billing_state)+'\\", street: [\\"'+(self.billing_street_address_1)+'\\", \\"'+(self.billing_street_address_2)+'\\"], telephone: \\"'+(self.billing_phone)+'\\", postcode: \\"'+(self.billing_zip_code)+'\\", city: \\"'+(self.billing_city)+'\\", firstname: \\"'+(self.billing_first)+'\\", lastname: \\"'+(self.billing_last)+'\\", saveInAddressBook: 0}, paymentMethod: {method: \\"authnetcim\\", additional_data: {save: false, cc_type: \\"'+(self.billing_card_type)+'\\", cc_cid: \\"'+(self.billing_card_cvn)+'\\", card_id: null, cc_number: \\"'+(self.billing_card_number)+'\\", cc_exp_year: \\"'+(self.billing_card_year)+'\\", cc_exp_month: \\"'+(self.billing_card_month)+'\\", platform: \\"Desktop web\\", version: \\"1.0\\", appVersion: \\"1.0\\", userId: \\"\\"}}, email: \\"'+(self.billing_email)+'\\", captchaToken: \\"'+(self.solveCaptcha())+'\\") {\\n    message\\n    status\\n    data\\n    rewardPoints\\n    __typename\\n  }\\n}\\n"}'

          signature_header=self.hashSignatureCalc(data)

          headers = {
              'Origin': 'https://www.paniniamerica.net',
              'x-amz-u-id': '',
              'Authorization': '',
              'content-type': 'application/json',
              'accept': '*/*',
              'User-Agent': self.APP_UA,
              'cart_id': self.CART_ID,
              'Signature': signature_header,
              'Referer': 'https://www.paniniamerica.net/cart.html?s=2',
              'x-amz-s-id': self.SESSION_ID,
              'x-amz-cart-id': self.CART_ID,
          }
          r = self.session.post('https://api.paniniamerica.net/onepanini', headers=headers, data=data)
          dictionary = json.loads(r.text)
          if dictionary['data']['guestPlaceOrder']['message'] == 'SUCCESS':
            self.ORDER_NUMBER=dictionary['data']['guestPlaceOrder']['data']
            print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,green+'Order Successfully Placed'.center(50,' ')+reset,lightblue+underline+self.ORDER_NUMBER+reset))
            started=True
          else:
            print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+dictionary['data']['guestPlaceOrder']['message']+" : Status Code "+str(r.status_code)+reset))
            time.sleep(1.5)
      except Exception as e:
          print ("({}) {} | [ {} ] {}".format(str(self.TASK_NUM).center(5, ' '), purple+str(time.asctime( time.localtime(time.time()) ))+reset,red+'Error'.center(50,' ')+reset,lightblue+underline+str(e)+" : Status Code "+str(r.status_code)+reset))
          print (r.text)
          time.sleep(self.DELAY)