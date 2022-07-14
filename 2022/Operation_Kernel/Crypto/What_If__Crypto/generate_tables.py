sbox = [225, 215, 45, 11, 70, 238, 109, 46, 159, 235, 57, 173, 90, 53, 85, 114, 245, 40, 78, 2, 71, 229, 199, 201, 58, 42, 177, 76, 210, 246, 12, 27, 26, 208, 243, 73, 92, 200, 206, 102, 217, 207, 17, 14, 147, 101, 170, 32, 10, 255, 80, 82, 24, 61, 95, 43, 124, 122, 216, 115, 205, 218, 75, 227, 239, 175, 152, 113, 74, 224, 248, 194, 97, 155, 91, 125, 249, 3, 25, 51, 103, 213, 204, 104, 63, 244, 145, 44, 160, 106, 21, 94, 222, 48, 121, 165, 171, 202, 31, 203, 29, 230, 156, 240, 168, 34, 129, 182, 234, 185, 241, 123, 33, 163, 15, 9, 0, 99, 7, 178, 49, 186, 154, 126, 148, 141, 130, 250, 67, 41, 232, 195, 52, 56, 118, 105, 22, 242, 184, 226, 64, 254, 162, 191, 66, 138, 20, 132, 72, 39, 221, 146, 161, 237, 86, 153, 166, 5, 120, 54, 81, 38, 77, 47, 19, 189, 4, 36, 128, 50, 111, 180, 1, 140, 13, 149, 172, 107, 181, 100, 169, 187, 83, 117, 192, 143, 139, 197, 190, 219, 136, 212, 251, 228, 231, 62, 179, 8, 60, 79, 84, 211, 144, 18, 188, 89, 35, 28, 158, 96, 30, 174, 151, 23, 112, 116, 87, 253, 127, 65, 133, 236, 220, 247, 252, 157, 55, 193, 209, 137, 196, 164, 233, 167, 16, 134, 69, 59, 98, 68, 135, 198, 223, 88, 150, 6, 142, 93, 131, 119, 108, 214, 176, 110, 183, 37]
pbox = [2, 5, 7, 4, 1, 0, 3, 6]

def xor(a, b):
    res = []
    for ac, bc in zip(a, b):
        res.append(ac^bc)
    return res

def encryptBlock(key, block):
    key = list(key)
    l = list(block[:8])
    r = list(block[8:])

    for iround in range(6):
        keybyte = key.pop()
        print("Round with", keybyte, bytes(l+r).hex())
        for isubround in range(4):
            f = []
            for i in range(8):
                f.append(sbox[l[i] ^ keybyte])
                keybyte = (keybyte + 1) % 256
            f = [f[pbox[i]] for i in range(8)]
            l, r = xor(r, f), l
    print("Result", bytes(l+r).hex())
    return bytes(l+r)

def crypt_block(block, a=39, b=58, c=18):
    l = list(block[:8])
    r = list(block[8:])

    l,r = round(a, l, r)
    l,r = round(b, l, r)
    l,r = round(c, l, r)

    return bytes(l+r)

def round(keybyte, l, r,):
    for isubround in range(4):
        f = []
        for i in range(8):
            f.append(sbox[l[i] ^ keybyte])
            keybyte = (keybyte + 1) % 256
        f = [f[pbox[i]] for i in range(8)]
        l, r = xor(r, f), l
    
    return (l,r)

def decrypt_block(block, a=77, b=158, c=249):
    l = list(block[:8])
    r = list(block[8:])

    l,r = reverse_rounds(a, l, r)
    l,r = reverse_rounds(b, l, r)
    l,r = reverse_rounds(c, l, r)

    return bytes(l+r)

def reverse_rounds(keybyte, l, r):
    l,r = reverse_round(keybyte, l, r, 3)
    l,r = reverse_round(keybyte, l, r, 2)
    l,r = reverse_round(keybyte, l, r, 1)
    l,r = reverse_round(keybyte, l, r, 0)

    return (l,r)

def reverse_round(keybyte, l, r, n=3):
    f = []
    keybyte = (keybyte + n*8) % 256
    for i in range(8):
        f.append(sbox[r[i] ^ keybyte])
        keybyte = (keybyte + 1) % 256

    f = [f[pbox[i]] for i in range(8)]

    r, l = xor(l, f), r

    return (l,r)


f_part1 = open("hashes_part1.txt", "w")
f_part2 = open("hashes_part2.txt", "w")

offset = 2

cipher = open("test.xlsx.enc", "rb").read()

plain = open("Témoin.xlsx", "rb").read()


ctr = (int.from_bytes(cipher[0:16], 'big') + offset).to_bytes(16, 'big')
encrypted_bytes = bytes(xor(cipher[(offset + 1) * 16:(offset + 2) * 16], plain[offset * 16:(offset + 1) * 16]))

looking_for_a = True
looking_for_b = True
write_to_files = False
good_hash = "e8167bc0991aa64cdd33133917b26c5a"

for a in range(256):
    print(str(a), "/ 255")
    for b in range(256):
        for c in range(256):
            hash_crypt = crypt_block(ctr, a, b, c).hex()
            hash_decrypt = decrypt_block(encrypted_bytes, a, b, c).hex()
            if(looking_for_a and hash_crypt == good_hash):
                print("A: " + str(a) + " " + str(b) + " " + str(c))
                looking_for_a = False
            if(looking_for_b and hash_decrypt == good_hash):
                print("B: " + str(a) + " " + str(b) + " " + str(c))
                looking_for_b = False
            if(not looking_for_a and not looking_for_b ):
                exit()
            if write_to_files:
                f_part1.write(hash_crypt + "\n")
                f_part2.write(hash_decrypt + "\n")

# Then run 
# awk 'NR==FNR{a[$4];next} ($4 in a)' hashes_part1.txt hashes_part2.txt 
# to get the hash

encryptBlock(bytes.fromhex("7823743b2937"), ctr)
# Debug:
# - CRT good
# - inverted key ??


# A: 44 209 42
# B: 43 221 178

a, b, c = (44, 209, 42)
d, e, f = (43, 221, 178)
#print(crypt_block(ctr, a, b, c).hex())
#print(decrypt_block(encrypted_bytes, d, e, f).hex())
key = [d, e, f, c, b, a]
print(bytes(key).hex())

f_part1.close()
f_part2.close()