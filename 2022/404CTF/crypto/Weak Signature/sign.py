import sys
import base64
#from secret import private_key

# Script for signing and verifying signed archives
mod = 221027607696016055330225199730004315633371808272167570987738708218816159833989480355901373361425282092914736310694029777936753927631812865622326955729592220642870561983138852634957728096291312307092550755716648880511833062740232861937708219741536005110883882372419034097193889630562360199603238619292770230484188772936262259410362789470181350351169944338502734560511300850685040238166004812599312697863279097878240430563714732124632651690886061257136157390268372745145428925223780181129620285589838270820282051669863964181353006744093479768868790988029676360187172005933366198639891820146811651748962622102323334597

def checksum(data: bytes) -> int:
    # Sum the integer value of each byte and multiply the result by the length
    chksum = sum(data) * len(data)

    return chksum
def complete(data: bytes, size: int, sm: int):
    n = size - len(data) - 1
    sm -= sum(data)
    c = chr(int(sm/n)) 
    for i in range(n):
        data += c.encode("utf-8")
        sm -= ord(c)
    data += chr(sm).encode("utf-8")
    return data

def check_signature(data: bytes, signature: int, mod: int) -> bool:
    # In our case, public key exponent is always 65537
    to_check = pow(signature, 65537, mod)

    # Compute the actual checksum
    chksum = checksum(data)

    return chksum == to_check



def solve():
    with open("script.py.zsig", "rb") as f:
        magic = f.read(5)
        if magic != b"\x01ZSig":
            return False
        
        f.read(1)
        signature = int.from_bytes(f.read(300), "big")

        f.read(1)
        size = int.from_bytes(f.read(4), "big")

        f.read(1)
        data = f.read()
        print(len(data), checksum(data), sum(data))
        cmd = b'print("exploit") #'
        cmd = b'f=open("./flag.txt");print(f.read()) #'
        
        payload = complete(cmd, len(data), sum(data))
        print(payload)
        print(check_signature(payload, signature, mod)) 

        # building file 
        with open("out_file.py.zsig", "wb+") as out:
          signature_bytes = signature.to_bytes(300, "big")

          size_bytes = len(payload).to_bytes(4, "big")
          out_bytes = b"\x01ZSig\x02" + signature_bytes + b"\x03" + size_bytes + b"\x04" + payload 
          
          out.write(out_bytes)
          b64 = base64.b64encode(out_bytes) 
          print(b64.decode("utf-8"))
            
solve()