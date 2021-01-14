import radio
import microbit
from microbit import sleep
from microbit import uart
from microbit import display
import random

radio.on()

connect = False
key = "IY546G6ZAubNFiua4zhef78p4afeaZRG"

uart.init(baudrate=115200, bits=8,parity=None, stop=1)

#def radio_send_request(request): 
#    display.set_pixel(3, 3, 5)
#    request = str(request)
#   radio.send(str(request))
#    return True

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
    #Inversion de l'ordre des caractères
    msg = str(msg)
    translated = ''
    while i >= 0:
        translated = translated + msg[i]
        i = i - 1
    return translated
"""
def cipher_key(msg, key):
    #XOR de la clée avec le message
    result = ""
    key_tmp = str(key)
    #key_tmp = str(key_tmp) + str(key) + str(key) + str(key) 
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
    return result"""

def cipher_key(msg, key):
    result = ""
    key_tmp = key
    bin_msg = map(bin,bytearray(msg))

    z = 0
    for bit_msg in (list(bin_msg)):
        z += 1

    while len(key_tmp) <= z:
        key_tmp += key
    key_tmp += key
    #print("len_key ", len(key_tmp))
    bin_key = map(bin,bytearray(key_tmp))
    bin_key = list(bin_key)

    #print("key",key_tmp)
    bin_msg = map(bin,bytearray(msg))

    i = 0
    for bit_msg in list(bin_msg):
        #print("bit")
        bit_msg = int(bit_msg)
        bit_key = int(bin_key[i])
        tmp = bit_msg ^ bit_key

        result += chr(tmp)
        i += 1
    return result




def encrypt(msg):
    msg = str(msg)
    i =  len(msg) - 1
    msg = reverse(msg, i)
    msg = cipher_key(msg, key)
    return msg

def decrypt(msg):
    msg = str(msg)
    i =  len(msg) - 1
    msg = cipher_key(msg, key)
    msg = reverse(msg, i)
    return msg
    
def send(msg):
    radio.send_bytes(msg)
    
def send_key(key):
    radio.send_value("key",key)

while True:
    UARTmessage = uart.read()
    
    if UARTmessage is None:
        continue


    elif UARTmessage:
        #Quand un message UART est reçu, on initialise la connexion si ça n'a pas été fait
        if connect ==  False:
            send_msg="key"+key
            radio.send(send_msg)

        #Chiffrement et envoi du message UART
        e_msg = encrypt(str(UARTmessage))
        send_msg = "msg"+e_msg
        #send_msg = "msg"+str(UARTmessage)
        radio.send(send_msg)
        microbit.display.scroll("UART Send", wait=False, loop=False)
    
    receivedMsg = radio.receive()

    if receivedMsg is None:
        continue
    elif receivedMsg:
        p_msg = parse(receivedMsg)
        
        #Si l'aquittement de réception de la clé est reçu, on envoie un numéro de channel définit aléatoirement
        if p_msg.type == "key":
            if p_msg.msg == "OK":
                random_channel = random.randint(0,83)
                #msg = encrypt("10")
                e_msg = encrypt(str(random_channel))
                send_msg="ch1"+e_msg
                radio.send(send_msg)
            else:
                send_msg="key"+key
                radio.send(send_msg)

        #Si l'acquittement de réception du channel est reçu, on notifie de la bonne mise en place de la connexion
        if p_msg.type == "ch1":
            msg = decrypt(p_msg.msg)
            if msg == "OK":
                e_msg = encrypt("established")
                send_msg ="ch2"+e_msg
                radio.config(channel=10)
                #radio.config(channel=int(random_channel))
                radio.send(send_msg)
                microbit.display.scroll("ACK", wait=False, loop=False)
                sleep(100)
                connect = True
            else:
                send_msg="key"+key
                radio.send(send_msg)
                microbit.display.scroll("Retry", wait=False, loop=False)
