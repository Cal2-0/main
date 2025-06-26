'''a=1
p = 23
g = 5

        
while a!=0:
    c=0
    b=''
    a=int(input('enter Option \n1.Encrypt \n2.Decrypt \n3.Find your key \n0.quit \n--->'))
    print()
    print()
    if a==1:
        x = input("Enter the message to be Encrypted \n--> ")
        b = ''
        p = 23
        g = 5

        priv = int(input("Enter your private key: "))
        other_pub = int(input("Enter other party's public key: "))  # DH exchange

        s = pow(other_pub, priv, p)  # shared key using DH
        a = {}

        for i in x:
            if i != ' ':
                a[i] = x.count(i)

        mi = min(a.values())
        ma = max(a.values())

        factor = ((mi * ma) * s)

        en = ''
        for i in x:
            if i == ' ':
                en+=' ' # preserve spaces
            else:
                val = (ord(i)* factor)
                en+=(str(val))  # store as string
        en=en+('009900')+str(mi*s)+('009900')+str(ma*s)
        print("\nEncrypted message:")
        print(en)

    if a==2:
        decrypted = ''
        ex1=input("\nPaste the encrypted message: ")
        encrypted_input = ex1.split()
        priv2 = int(input("Enter your private key again: "))
        sender_pub = int(input("Enter sender's public key: "))

        s2 = pow(sender_pub, priv2, p)  # should match original shared key
        a2 = {}

        ex1=ex1.split("009900")
        print(ex1)

        mi2 = int(ex1[1])
        ma2 = int(ex1[2])

        factor2 = ((mi2 * ma2) * s2)

        for val in encrypted_input:
            if val == ' ':
                decrypted += ' '
            else:
                num = int(val)
                original_ord = num // ( factor2)
                decrypted += chr(original_ord)

        print("\nDecrypted message:")
        print(decrypted)
    if a==3:
        x=int(input("enter ur priv key"))
        print(g**(x)%p)
    if a==0:
        break
    
'''
a = 1
p = int('''
FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E08
8A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD
3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E
7EC6F44C42E9A63A3620FFFFFFFFFFFFFFFF
'''.replace('\n', '').replace(' ', ''), 16)

g = 5

while a != 0:
    c = 0
    b = ''
    a = int(input('Enter Option \n1. Encrypt \n2. Decrypt \n3. Find your key \n0. Quit \n---> '))
    print()
    print()
    print()

    if a == 1:
        x = input("Enter the message to be Encrypted \n--> ")
        priv = int(input("Enter your private key: "))
        other_pub = int(input("Enter other party's public key: "))  # DH exchange

        s = pow(other_pub, priv, p)  # shared key using DH
        freq_map = {}

        for i in x:
            if i != ' ':
                freq_map[i] = x.count(i)

        mi = min(freq_map.values())
        ma = max(freq_map.values())

        factor = ((mi * ma) * s)

        en = []
        for i in x:
            if i == ' ':
                en.append('-1')  # changed from 'SPACE' to '-1'
            else:
                val = (ord(i) * factor)
                en.append(str(val))

        # append markers
        en.append('009901' + str(mi * s))
        en.append('009900' + str(ma * s))

        encrypted_str = ' '.join(en)
        print("\nEncrypted message:")
        print(encrypted_str)
        print()
        print()

    elif a == 2:
        decrypted = ''
        ex1 = input("\nPaste the encrypted message: ").split()
        priv2 = int(input("Enter your private key again: "))
        sender_pub = int(input("Enter sender's public key: "))

        s2 = pow(sender_pub, priv2, p)  # shared key

        # Extract last two items for mi and ma
        mi_str = ex1[-2]
        ma_str = ex1[-1]

        if not (mi_str.startswith('009901') and ma_str.startswith('009900')):
            print("Error: Invalid encryption format.")
            continue

        mi2 = int(mi_str[6:]) // s2  # fix slicing!
        ma2 = int(ma_str[6:]) // s2  # fix slicing!

        factor2 = ((mi2 * ma2) * s2)

        # Now decrypt all except the last two items
        encrypted_values = ex1[:-2]

        for val in encrypted_values:
            if val == '-1':  # changed from 'SPACE' to '-1'
                decrypted += ' '
            else:
                num = int(val)
                original_ord = num // factor2
                if 0 <= original_ord <= 1114111:
                    decrypted += chr(original_ord)
                else:
                    decrypted += '?'  # fallback

        print("\nDecrypted message:", decrypted)
        print()
        print()

    elif a == 3:
        x = int(input("Enter your private key: "))
        print("Your public key:", pow(g, x, p))
        print()
        print()

    elif a == 0:
        break
    print("===============================================================================")
