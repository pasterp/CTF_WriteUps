#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import binascii
import hashlib
import json
import random

sbox = [225, 215, 45, 11, 70, 238, 109, 46, 159, 235, 57, 173, 90, 53, 85, 114, 245, 40, 78, 2, 71, 229, 199, 201, 58, 42, 177, 76, 210, 246, 12, 27, 26, 208, 243, 73, 92, 200, 206, 102, 217, 207, 17, 14, 147, 101, 170, 32, 10, 255, 80, 82, 24, 61, 95, 43, 124, 122, 216, 115, 205, 218, 75, 227, 239, 175, 152, 113, 74, 224, 248, 194, 97, 155, 91, 125, 249, 3, 25, 51, 103, 213, 204, 104, 63, 244, 145, 44, 160, 106, 21, 94, 222, 48, 121, 165, 171, 202, 31, 203, 29, 230, 156, 240, 168, 34, 129, 182, 234, 185, 241, 123, 33, 163, 15, 9, 0, 99, 7, 178, 49, 186, 154, 126, 148, 141, 130, 250, 67, 41, 232, 195, 52, 56, 118, 105, 22, 242, 184, 226, 64, 254, 162, 191, 66, 138, 20, 132, 72, 39, 221, 146, 161, 237, 86, 153, 166, 5, 120, 54, 81, 38, 77, 47, 19, 189, 4, 36, 128, 50, 111, 180, 1, 140, 13, 149, 172, 107, 181, 100, 169, 187, 83, 117, 192, 143, 139, 197, 190, 219, 136, 212, 251, 228, 231, 62, 179, 8, 60, 79, 84, 211, 144, 18, 188, 89, 35, 28, 158, 96, 30, 174, 151, 23, 112, 116, 87, 253, 127, 65, 133, 236, 220, 247, 252, 157, 55, 193, 209, 137, 196, 164, 233, 167, 16, 134, 69, 59, 98, 68, 135, 198, 223, 88, 150, 6, 142, 93, 131, 119, 108, 214, 176, 110, 183, 37]
pbox = [2, 5, 7, 4, 1, 0, 3, 6]

class Encryptor(object):
    def __init__(self, passphrase):
        self.key = passphrase.encode()

    def generateKey(self):
        self.key = hashlib.sha256(self.key).digest()[:6]
        return self.key

    def xor(self, a, b):
        res = []
        for ac, bc in zip(a, b):
            res.append(ac^bc)
        return res

    def encryptBlock(self, block, key_bytes=False):
        if not key_bytes:
            key = list(self.generateKey())
        else:
            self.key = key_bytes
            key = list(self.key)

        print(block.hex(), self.key.hex())

        l = list(block[:8])
        r = list(block[8:])
        for iround in range(6):
            keybyte = key.pop()
            for isubround in range(4):
                f = []
                for i in range(8):
                    f.append(sbox[l[i] ^ keybyte])
                    keybyte = (keybyte + 1) % 256
                f = [f[pbox[i]] for i in range(8)]
                l, r = self.xor(r, f), l
        return bytes(l+r)

    def encrypt(self, plaintext):
        while len(plaintext)%16:
            plaintext += b'\0'

        ctr = random.getrandbits(128)

        encrypted = ctr.to_bytes(16, 'big')
        for i in range(0, len(plaintext), 16):
            encryptedBlock = self.encryptBlock(ctr.to_bytes(16, 'big'))
            encrypted += bytes(self.xor(plaintext[i:i+16], encryptedBlock))
            ctr += 1
        return encrypted

    def decrypt(self, cipher):
        assert(len(cipher)%16 == 0)

        ctr = int.from_bytes(cipher[:16], 'big')
        decoded = b""
        for i in range(16, len(cipher), 16):
            block = self.encryptBlock(ctr.to_bytes(16, 'big'))
            decoded += bytes(self.xor(cipher[i:i+16], block))
            ctr += 1
        return decoded

    def partial_decrypt(self, cipher, key_bytes, offset = 0):
        # offset in number of rounds
        assert(len(cipher)%16 == 0)

        ctr = int.from_bytes(cipher[:16], 'big')
        ctr += offset 
        decoded = b""

        for i in range(16+16*offset, len(cipher), 16):
            block = self.encryptBlock(ctr.to_bytes(16, 'big'), key_bytes)
            decoded += bytes(self.xor(cipher[i:i+16], block))
            ctr += 1
            key_bytes = hashlib.sha256(key_bytes).digest()[:6]
        return decoded
        

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', help='file path to encrypt')
    parser.add_argument('passphrase', help='Passphrase used to encrypt file')
    parser.add_argument('-O', '--output-file', help='Specify the output file')
    parser.add_argument('-d', '--decrypt', action='store_true', dest="decrypt", help="Decrypt the file")
    parser.add_argument('--offset', help="Offset for partial decryption")
    parser.add_argument('--key', help="Key bytes as hex for partial decryption")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    print('Welcome to Encryptor')
    if args.decrypt:
        print('Decrypting %s using :' % args.file, args.passphrase)
        cipher = open(args.file, 'rb').read()
        passphrase = args.passphrase

        if args.key:
            plaintext = Encryptor(passphrase).partial_decrypt(cipher, bytes.fromhex(args.key), int(args.offset))
        else:
            plaintext = Encryptor(passphrase).decrypt(cipher)

        if args.output_file:
            print("Plaintext data saved in : %s" % args.output_file)
            f = open(args.output_file, 'wb')
            f.write(plaintext)
            f.close()
        else:
            print('Your file after decryption is', plaintext.hex())
    else:
        print('Encrypting %s using :' % args.file, args.passphrase)
        plaintext = open(args.file, 'rb').read()
        passphrase = args.passphrase
        ciphertext = Encryptor(passphrase).encrypt(plaintext)
        
        if args.output_file:
            print("Cipher data saved in : %s" % args.output_file)
            f = open(args.output_file, 'wb')
            f.write(ciphertext)
            f.close()
        else:
            print('Your file after encryption is', ciphertext.hex())
