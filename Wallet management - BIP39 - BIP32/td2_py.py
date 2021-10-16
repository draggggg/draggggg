# -*- coding: utf-8 -*-
"""TD2.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YSTMyVQ2pxYExN0UiNo0H52ST_8y4HTC
"""

#Créer un entier aléatoire pouvant servir de seed à un wallet de façon sécurisée
import secrets
sec=secrets.randbits(128)
print('nombre sécurisé de 128 bits généré aléatoirement :',sec,'\n') #on obtient ici notre nombre de taille  bits généré aléatoirement 

secbin=bin(sec) #fonction bin pour convertir un décimal en binaire 
secbinbon = secbin[2:len(secbin)] # secbinbon est notre chiffre binaire sans le 0b
print('le même nombre généré en binaire :',secbinbon,'\n')



b= secbinbon
#b= '1110000010110010100100011101001100110001110111111011011001010110111111001101010110111011111011000101001001001100011011111011000000'
bcomp='0' #cas 131 par defaut (le cas 132 n'existe pas)
if (132-len(b) == 2): #cas 130
  bcomp = '00'
if (132-len(b) == 3): #etc..
  bcomp = '000'
if (132-len(b) == 4): 
  bcomp = '0000'
if (132-len(b) == 5): 
  bcomp = '00000'
if (132-len(b) == 6): 
  bcomp = '000000'
if (132-len(b) == 7): 
  bcomp = '0000000'
if (132-len(b) == 8): 
  bcomp = '00000000'
if (132-len(b) == 9): 
  bcomp = '000000000'
if (132-len(b) == 10): 
  bcomp = '0000000000'
if (132-len(b) == 11): 
  bcomp = '00000000000'
if (132-len(b) == 12): 
  bcomp = '000000000000'
b = ''.join((b,bcomp))

print('le même nombre généré en binaire sur 132bits', b,'\n')

with open("englishlist.txt","r") as f:
  wordlist= [w.strip() for w in f.readlines()] 
  seed = []
  for i in range(len(b)//11): #12 itérations
    indx = int(b[11*i:11*(i+1)],2) #l'index correspond à la chaine de 11 caractères 
    seed.append(wordlist[indx]) #on ajoute le mot correspondant à l'index à chaque itération
  print('la seed de 12 mots générée :', seed)

import urllib.request as urllib
import json

# Charger le dictionnaire bip39
wordListUrl = "https://raw.githubusercontent.com/bitcoinjs/bip39/master/src/wordlists/english.json"
wordlist = list(json.load(urllib.urlopen(wordListUrl)))

# Créer 2 dictionnaires 
def createDic():
    alphadic = {}  

    linenumber = 0
    for line in wordlist:
        alphadic[line] = linenumber #le mot est associé au numéro 
        linenumber += 1

    return alphadic 
# mnemonic decoding algorithm, decode a mnemonic string back to the orinal hex number

def decode(s):
    alphadic = createDic() #alphadic contient tous les numéros associés aux mots du bip39
    l=[]
    

    for word in s.split(): #s est la phrase rentrée par l'utilisateur 
        w = bin(alphadic[word])[2:]  #w nombre binaire correspondant au mot respectif à chaque itération
        a = "0" * (11 - len(w) ) + w #a est le nombre binaire de 11 bits correspondant à un mot de la seed, on rajoute le nombre de 0 nécéssaire si le nombre ne fait pas 11 bits (méthode plus élégante qu'au dessus)
        l.append(a) 
    r = "".join(l) #r est la chaine de caracteres constituées de notre seed traduite en binaire
    out = ""
    for i in range(0, len(r), 4):
        out += hex(int(r[i: i + 4], 2))[2:] #ici on convertit simplement notre chaine de caractères en hexadécimal
    return out[:-1] #on obtient alors notre entropie ! Vous pouvez verifiez sur iancoleman

if __name__ == "__main__":
  # TODO: remove the trailing extra 0s
  print('Merci de rentrer une seed memnonique de 12 mots (english) exemple : abandon world act adult attract hello home run three trade twin wheel \n')
seed = str(input())
print('\n')
print('L entropy est :' ,
      decode(seed))

#!pip install ecdsa

import binascii
import hmac
import hashlib
import ecdsa
import struct
from ecdsa.curves import SECP256k1
from ecdsa.ecdsa import int_to_string, string_to_int

class B58():

    def b58encode(v):
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        p, acc = 1, 0
        for c in reversed(v):
            acc += p * c
            p = p << 8

        string = ""
        while acc:
            acc, idx = divmod(acc, 58)
            string = alphabet[idx : idx + 1] + string
        return string

#Partie1 Master Key
seed = binascii.unhexlify("000102030405060708090a0b0c0d0e0f")  # Première chose, on genere une seed de caractères hexadécimaux de (taille 128 bits ici)
I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest() #On génère ensuite I qui est le hash de notre seed à l’aide de la clé bitcoin “Bitcoin Seed”
Il, Ir = I[:32], I[32:]  # On sépare I en deux séquences Gauche et Droite 
print(I)

# Partie 2 Master Key ; Serialization 

chain = Ir # partie droite de HMAC, c'est notre chain code !
xprv = binascii.unhexlify("0488ade4") # Version de string  pour les extended private keys
xpub = binascii.unhexlify("0488b21e") # Version de string pour les  extended public keys
depth = b"\x00" # Child depth ici profondeur de 0 car premier parent (1 pour enfant, 2 pour sous enfant etc..)
fpr = b'\0\0\0\0' # Parent fingerprint
index = 0 # index d'enfant
child = struct.pack('>L', index)  # notre enfant à partir de l'index


#Géneration de data_priv et data_pub
secret = Il #  partie gauche de HMAC: sera utilisé pour générer la k_priv
k_priv = ecdsa.SigningKey.from_string(secret, curve=SECP256k1)
K_priv = k_priv.get_verifying_key()
data_priv = b'\x00' + (k_priv.to_string())  # ser256(p): pour serializer un entier comme une sequence de 32 bits
# serilization de la paire coordonnée P = (x,y) 
if K_priv.pubkey.point.y() & 1: #test de parité
    data_pub= b'\3'+int_to_string(K_priv.pubkey.point.x())
else:
    data_pub = b'\2'+int_to_string(K_priv.pubkey.point.x())


raw_priv = xprv + depth + fpr + child + chain + data_priv #on s'appuie sur la doc : xprv = version bytes ; depth = 0x00 for master nodes ; fpr = fingerprint ; child = child number ; chain = chain code ; data_priv = private key
raw_pub = xpub + depth + fpr + child + chain + data_pub #idem mais cette fois ci avec xpub et public key



# Double hash des clés publiques et clés privéesen utilisant SHA256
hashed_xprv = hashlib.sha256(raw_priv).digest()
hashed_xprv = hashlib.sha256(hashed_xprv).digest() # méthode barbare mais comp'éhensible
hashed_xpub = hashlib.sha256(raw_pub).digest()
hashed_xpub = hashlib.sha256(hashed_xpub).digest()

# Ajoute 4 bits à checksum
raw_priv += hashed_xprv[:4]
raw_pub += hashed_xpub[:4]

# Affichage
print('\n')
print('master private key :',B58.b58encode(raw_priv),'\n')
print('master public key :' ,B58.b58encode(raw_pub),'\n')
print('chain code (hex):' ,chain.hex(),'\n')

#@title Titre par défaut
#!pip install Mnemonic
#!pip install bip32utils
from mnemonic import Mnemonic
import bip32utils

mnemon = Mnemonic('english')
#words = mnemon.generate(256)
#print(words)
#mnemon.check(words)
#seed = mnemon.to_seed(words)
seed = mnemon.to_seed(b'abandon amount liar amount expire adjust cage candy arch gather drum buyer')
print(f'BIP39 Seed: {seed.hex()}\n')

root_key = bip32utils.BIP32Key.fromEntropy(seed)

child_key = root_key.ChildKey(0).ChildKey(0)
child_address = child_key.Address()
child_public_hex = child_key.PublicKey().hex()
child_private_wif = child_key.WalletImportFormat()

child_key2 = root_key.ChildKey(0).ChildKey(2)
child_address2 = child_key2.Address()
child_public2_hex = child_key2.PublicKey().hex()
child_private2_wif = child_key2.WalletImportFormat()

print('Clef enfant:')
print(f'\tAddress: {child_address}')
print(f'\tPublic (hex): {child_public_hex}')
print(f'\tPrivate (wif) : {child_private_wif}\n')

print('Clef enfant à l index 2:')
print(f'\tAddress: {child_address2}')
print(f'\tPublic (hex): {child_public2_hex}')
print(f'\tPrivate (wif) : {child_private2_wif}')

"""Si un pirate met la main sur une clé privée enfant et la clé xpub du compte, le pirate peut recalculer la clé xprv du compte et ainsi avoir accès à chaque clé privée et publique descendant du niveau du compte."""