# -*- coding: utf-8 -*-
"""TD2.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YSTMyVQ2pxYExN0UiNo0H52ST_8y4HTC
"""

import secrets


import urllib.request as urllib
import json
#!pip install ecdsa

import binascii
import hmac
import hashlib
import ecdsa
import struct
from ecdsa.curves import SECP256k1
from ecdsa.ecdsa import int_to_string, string_to_int



#!pip install Mnemonic
#!pip install bip32utils
from mnemonic import Mnemonic
import bip32utils

def mainprogram(argument):
    if(argument==1):
      
      sec=secrets.randbits(128)
      print('nombre sécurisé de 128 bits généré aléatoirement :',sec,'\n') #on obtient ici notre nombre de taille  bits généré aléatoirement 
    
    
    elif(argument==2):
      sec=secrets.randbits(128)
      secbin=bin(sec) #fonction bin pour convertir un décimal en binaire 
      secbinbon = secbin[2:len(secbin)] # secbinbon est notre chiffre binaire sans le 0b
      print('Le nombre généré en binaire :',secbinbon,'\n')
      b= secbinbon
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

      print('Le nombre généré en binaire sur 132bits', b,'\n')
      #AJOUTER LE FICHIER SI VOUS VOULEZ LE RUN SUR COLLAB
      with open("englishlist.txt","r") as f:
        wordlist= [w.strip() for w in f.readlines()] 
        seed = []
        for i in range(len(b)//11): #12 itérations
          indx = int(b[11*i:11*(i+1)],2) #l'index correspond à la chaine de 11 caractères 
          seed.append(wordlist[indx]) #on ajoute le mot correspondant à l'index à chaque itération
        print('La seed de 12 mots générée :', seed)
      


    elif(argument==3):
      print('Merci de rentrer une seed memnonique de 12 mots (english) exemple : abandon world act adult attract hello home run three trade twin wheel \n')
      seed = str(input())
      print('\n')
      print('L entropie est :' ,
            decode(seed))




    elif(argument==4):


      print("Voulez vous utiliser une entropie pré-définie (tapez 1) ou voulez vous entrer votre entropie en forme hexadécimale (tapez 2) ?")
      choixentropie = int(input())
      if(choixentropie == 1):
        #Partie1 Master Key
        seed11="000102030405060708090a0b0c0d0e0f"
        seed = binascii.unhexlify("000102030405060708090a0b0c0d0e0f")  # Première chose, on genere une seed de caractères hexadécimaux de (taille 128 bits ici)
        I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest() #On génère ensuite I qui est le hash de notre seed à l’aide de la clé bitcoin “Bitcoin Seed”
        Il, Ir = I[:32], I[32:]  # On sépare I en deux séquences Gauche et Droite 
        print("On a généré la seed suivante", seed11)
        print("Notre HMAC est", I)

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


      if(choixentropie == 2):
        print("Entrez votre seed de 128 bits sous format hexadécimal, exemple : 000102030405060708090a0b0c0d0e0f")
        seed1 = str(input())
        #Partie1 Master Key
        seed = binascii.unhexlify(seed1)  # Première chose, on genere une seed de caractères hexadécimaux de (taille 128 bits ici)
        I = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest() #On génère ensuite I qui est le hash de notre seed à l’aide de la clé bitcoin “Bitcoin Seed”
        Il, Ir = I[:32], I[32:]  # On sépare I en deux séquences Gauche et Droite 
        print("On a généré la seed suivante", seed1)
        print("Notre HMAC est", I)

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

    
    elif(argument==5):
      print("Voulez vous utiliser une seed pré-définie (tapez 1) ou voulez vous tapez votre propre seed mnémonique (tapez 2) ?")
      seedchoice = int(input())
      if(seedchoice == 1):
        mnemon = Mnemonic('english')
        seed = mnemon.to_seed(b'abandon amount liar amount expire adjust cage candy arch gather drum buyer')
        print(f'BIP39 Seed: {seed.hex()}\n')

        root_key = bip32utils.BIP32Key.fromEntropy(seed)

        child_key = root_key.ChildKey(0).ChildKey(0)
        child_address = child_key.Address()
        child_public_hex = child_key.PublicKey().hex()
        child_private_wif = child_key.WalletImportFormat()

        print('Clef enfant:')
        print(f'\tAddress: {child_address}')
        print(f'\tPublic (hex): {child_public_hex}')
        print(f'\tPrivate (wif) : {child_private_wif}\n')
      if(seedchoice == 2):
        mnemon = Mnemonic('english')
        print("Entrez votre seed de 12 mots avec les mots séparés d'un espace, exemple : abandon amount liar amount expire adjust cage candy arch gather drum buyer")
        seed1= str(input())
        seed = mnemon.to_seed(seed1)
        print(f'BIP39 Seed: {seed.hex()}\n')

        root_key = bip32utils.BIP32Key.fromEntropy(seed)

        child_key = root_key.ChildKey(0).ChildKey(0)
        child_address = child_key.Address()
        child_public_hex = child_key.PublicKey().hex()
        child_private_wif = child_key.WalletImportFormat()

        print('Clef enfant:')
        print(f'\tAddress: {child_address}')
        print(f'\tPublic (hex): {child_public_hex}')
        print(f'\tPrivate (wif) : {child_private_wif}\n')

      



    elif(argument==6):
        print("A quel index souhaitez vous énérer une clé enfant")
        n=int(input())

        print("Voulez vous utiliser une seed pré-définie (tapez 1) ou voulez vous tapez votre propre seed mnémonique (tapez 2) ?")
        seedchoice = int(input())
        if(seedchoice == 1):

          mnemon = Mnemonic('english')
          seed = mnemon.to_seed(b'abandon amount liar amount expire adjust cage candy arch gather drum buyer')
          print(f'BIP39 Seed: {seed.hex()}\n')

          root_key = bip32utils.BIP32Key.fromEntropy(seed)

          child_key = root_key.ChildKey(0).ChildKey(0)
          child_address = child_key.Address()
          child_public_hex = child_key.PublicKey().hex()
          child_private_wif = child_key.WalletImportFormat()



          child_key2 = root_key.ChildKey(0).ChildKey(n)
          child_address2 = child_key2.Address()
          child_public2_hex = child_key2.PublicKey().hex()
          child_private2_wif = child_key2.WalletImportFormat()


    
          print("Clef enfant à l index",n)
          print(f'\tAddress: {child_address2}')
          print(f'\tPublic (hex): {child_public2_hex}')
          print(f'\tPrivate (wif) : {child_private2_wif}') 
        
        if(seedchoice == 2):
          mnemon = Mnemonic('english')
          print("Entrez votre seed de 12 mots avec les mots séparés d'un espace, exemple : abandon amount liar amount expire adjust cage candy arch gather drum buyer")
          seed1= str(input())
          seed = mnemon.to_seed(seed1) 
          print(f'BIP39 Seed: {seed.hex()}\n')

          root_key = bip32utils.BIP32Key.fromEntropy(seed)

          child_key = root_key.ChildKey(0).ChildKey(0)
          child_address = child_key.Address()
          child_public_hex = child_key.PublicKey().hex()
          child_private_wif = child_key.WalletImportFormat()



          child_key2 = root_key.ChildKey(0).ChildKey(n)
          child_address2 = child_key2.Address()
          child_public2_hex = child_key2.PublicKey().hex()
          child_private2_wif = child_key2.WalletImportFormat()


    
          print("Clef enfant à l index",n)
          print(f'\tAddress: {child_address2}')
          print(f'\tPublic (hex): {child_public2_hex}')
          print(f'\tPrivate (wif) : {child_private2_wif}') 
    else:
      print("Commande non implémentée, veuillez essayer un chiffre valide")

                
      


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


if __name__ == "__main__":
    const=0
    while(const==0):
      print("Que voulez vous faire")
      print("1. Créer un entier aléatoire pouvant servir de seed à un wallet de façon sécurisée")
      print("2.Représenter cette seed en binaire et le découper en lot de 11 bits et Attribuer à chaque lot un mot selon la liste BIP 39 et afficher la seed en mnémonique")
      print("3. Permettre l’import d’une seed mnémonique")
      print("4. Extraire la master private key et le chain code et extraire la master public key")
      print("5. Générer une clé enfant")
      print("6. Générer une clé enfant à l’index N")


      argument = int(input())
      print(mainprogram(argument))

"""Si un pirate met la main sur une clé privée enfant et la clé xpub du compte, le pirate peut recalculer la clé xprv du compte et ainsi avoir accès à chaque clé privée et publique descendant du niveau du compte."""
