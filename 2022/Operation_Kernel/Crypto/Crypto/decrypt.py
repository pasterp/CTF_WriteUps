def xor(a, b):
    res = []
    for ac, bc in zip(a, b):
        res.append(ac^bc)
    return res

def decrypt(cipher, ctr):
    result = b""
    for i in range(0, len(cipher), 16):
        result += bytes(xor(cipher[i:i+16], ctr.to_bytes(16, 'big')))
        ctr += 1
    return result


f = open("CONFIDENTIEL.xlsx.enc", 'rb')
out = open("out.xlsx", "wb")
cipher = f.read()
ctr = int.from_bytes(cipher[:16], 'big')
data = decrypt(cipher[16:], ctr)
out.write(data)
out.close()
f.close()
