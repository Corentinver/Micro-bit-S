import radio
import microbit
from microbit import sleep
import random

radio.on()

connect = False
key = "IY546G6ZAubNFiua4zhef78p4afeaZRG"

class Msg:
    def __init__(self):
        self.msg = ""
        self.type = ""

def parse(msg):
    l = len(msg) - 1
    print("length: ", l)
    i = 0
    parse_msg = Msg()
    while i <= l:
        print("i", i)
        if i < 3:
            parse_msg.type += msg[i]
        if i  >= 3:
            parse_msg.msg += msg[i]
        i += 1
    return parse_msg

def reverse(msg, i):
    translated = ''
    while i >= 0:
        translated = translated + msg[i]
        i = i - 1
    return translated

def cipher_key(msg, key):
    result = ""
    key_tmp = str(key)
    while len(key) < len(msg):
        key_tmp = str(key_tmp) + str(key)

    key2 = ''
    for i in range(len(msg)):
        key2 += key_tmp[i]

    bin_msg = map(bin,bytearray(msg))
    bin_key = map(bin,bytearray(key2))
    bin_key = list(bin_key)
    i = 0
    for bit_msg in list(bin_msg):
        bit_msg = int(bit_msg)
        bit_key = int(bin_key[i])
        tmp = bit_msg ^ bit_key
        result += chr(tmp)
        i += 1
    return result

def encrypt(msg):
    i =  len(msg) - 1
    msg = reverse(msg, i)
    msg = cipher_key(msg, key)
    return msg

def decrypt(msg):
    i =  len(msg) - 1
    msg = cipher_key(msg, key)
    msg = reverse(msg, i)
    return msg
    
def send(msg):
    radio.send_bytes(msg)
    
def send_key(key):
    radio.send_value("key",key)

while True:
    if microbit.button_a.is_pressed():
        send_msg="key"+key
        radio.send(send_msg)
    receivedMsg = radio.receive()
    if receivedMsg:
        p_msg = parse(receivedMsg)
        
        if p_msg.type == "key":
            if p_msg.msg == "OK":
                microbit.display.scroll("Key Ok", wait=False, loop=False)
                random_channel = random.randint(0,83)
                #msg = encrypt("10")
                msg = encrypt(str(random_channel))
                send_msg="ch1"+msg
                radio.send(send_msg)
            else:
                send_msg="key"+key
                radio.send(send_msg)
        if p_msg.type == "ch1":
            msg = decrypt(p_msg.msg)
            if msg == "OK":
                microbit.display.scroll(random_channel, wait=False, loop=False)
                send_txt = encrypt("established")
                send_msg ="ch2"+send_txt
                #radio.config(channel=10)
                radio.config(channel=int(random_channel))

                radio.send(send_msg)
                microbit.display.scroll("Send", wait=False, loop=False)
                connect = True
            else:
                send_msg="key"+key
                radio.send(send_msg)