#!/bin/python3
import sqlite3
import time
import json
import requests
import urllib
import os
import signal
from threading import Timer


TOKEN = "1305342821:AAHUh-gq8ospT7vKvHIsnxiKrNKnSwcyFe0"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
products = ["apple", "orange", "banana"]
numbers = ["1", "2", "3"]
y_n = ["yes","no"]
start = ["start"]
state_and_chat_dict = {}
orders_dict = {}
chat_group = -1001464803179

def get_url(url):
    response = requests.get(url)
    return response.content.decode("utf8")


def get_json_from_url(url):
    content = get_url(url)
    return json.loads(content)


def get_updates(offset=None):
    url = URL + "getUpdates?timeout=100"
    if offset:
       url += "&offset={}".format(offset)
    return get_json_from_url(url)


def get_last_update_id(updates):
    #l = sorted(updates['result'], lambda u: u['update_id'], reverse=True)
    #return l[0] if l else -1
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard":keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def handle_updates(updates, order_iteration):
    choose_to_start = build_keyboard(start)
    text, chat = get_last_chat_id_and_text(updates)
    if chat not in state_and_chat_dict:
        add_chat(state_and_chat_dict, text, chat)
    if state_and_chat_dict[chat]["idle"] and text not in start:
        pass
    elif text in start and state_and_chat_dict[chat]["idle"] == True:
        order_iteration += 1
        state_and_chat_dict[chat]["order number"] = order_iteration
        make_order(orders_dict, order_iteration, chat)
        product_choise = build_keyboard(products)
        send_message("choose a product", chat, product_choise)
        state_and_chat_dict[chat]["idle"] = False
        state_and_chat_dict[chat]["products"] = True
    elif text in products and not state_and_chat_dict[chat]["numbers"]:
        orders_dict[order_iteration][chat]["product"] = text
        number_choise = build_keyboard(numbers)
        send_message("how many?", chat, number_choise)
        state_and_chat_dict[chat]["products"] = False
        state_and_chat_dict[chat]["numbers"] = True
    elif text in numbers and not state_and_chat_dict[chat]["y_n"]:
        orders_dict[order_iteration][chat]["quantity"] = text
        y_n_choise = build_keyboard(y_n)
        send_message("anything else?", chat, y_n_choise)
        state_and_chat_dict[chat]["numbers"] = False
        state_and_chat_dict[chat]["y_n"] = True
    elif text == "yes" and not state_and_chat_dict[chat]["products"]:
        order_iteration += 1
        make_order(orders_dict, order_iteration, chat)
        product_choise = build_keyboard(products)
        send_message("choose a product", chat, product_choise)
        state_and_chat_dict[chat]["y_n"] = False
        state_and_chat_dict[chat]["products"] =True
    else:
        start_choise = build_keyboard(start)
        send_message("by clicking start you can shop", chat, start_choise)
        state_and_chat_dict[chat]["idle"] = True
        state_and_chat_dict[chat]["product"] = False
        state_and_chat_dict[chat]["numbers"] = False
        state_and_chat_dict[chat]["y_n"] = False
    return order_iteration
    
    
def add_chat(state_and_chat_dict, text, chat):
    state_and_chat_dict[chat]={"idle": False, "products":False, "numbers":False, "y_n":False}
    if text == start or text == "yes":
        state_and_chat_dict[chat]["products"] = True
    elif text in products:
        state_and_chat_dict[chat]["numbers"] = True
    elif text in numbers:
        state_and_chat_dict[chat]["y_n"] = True
    else:
        state_and_chat_dict[chat]["idle"] = True

def make_order(orders_dict,order_num, chat):
    orders_dict[order_num] = {chat:{"product":"waiting", "quantity":"waiting"}}

def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["from"]["id"]
    return text, chat_id


def send_message(text, chat_id, reply_markup=None):
    text=urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=MarkDown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)

def write_orders_to_file():
    with open('orders.txt', 'w') as outfile:
        json.dump(orders_dict, outfile)
    print(time.ctime)
    Timer(5, write_orders_to_file).start()


def main():
    order_iteration = 0
    last_update_id = None
    select_start = build_keyboard(start)
    send_message("to shop, choose start", chat_group, select_start)
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"])>0:
            last_update_id = get_last_update_id(updates) + 1
            order_iteration = handle_updates(updates, order_iteration)
                
        time.sleep(0.5)
    write_orders_to_file()

if __name__ == '__main__' : 
    main()

