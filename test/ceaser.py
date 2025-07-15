#ceaser
'''
def encode(x,f):
    o=''
    for i in x:
        if i.isalnum()==False:
            o+=i
        else:
            o+=chr((ord(i))+f)
    return o
        


def decode(x,f):
    o=''
    for i in x:
        if i.isalnum()==False:
            o+=i
        else:
            o+=chr((ord(i))-f)
    return o
        

while True:
    x=input()
    f=int(input("enter the shift"))
    print(decode(x,f))

#vign
def vencode(x, f):
    l = {
        'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5,
        'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11,
        'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17,
        's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23,
        'y': 24, 'z': 25
    }

    rev = {v: k for k, v in l.items()}  # Reverse map

    c = ''
    x = x.lower()
    f = f.lower()
    le = len(f)
    op = 0

    for i in x:
        if not i.isalpha():
            c += i
        else:
            key_char = f[op % le]
            shifted_index = (l[i] + l[key_char]) % 26
            c += rev[shifted_index]
            op += 1

    print(c)
    return c

        


def vdecode(x,f):
    l = {
        'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5,
        'g': 6, 'h': 7, 'i': 8, 'j': 9, 'k': 10, 'l': 11,
        'm': 12, 'n': 13, 'o': 14, 'p': 15, 'q': 16, 'r': 17,
        's': 18, 't': 19, 'u': 20, 'v': 21, 'w': 22, 'x': 23,
        'y': 24, 'z': 25
    }

    rev = {v: k for k, v in l.items()}  # Reverse map

    c = ''
    x = x.lower()
    f = f.lower()
    le = len(f)
    op = 0

    for i in x:
        if not i.isalpha():
            c += i
        else:
            key_char = f[op % le]
            shifted_index = (l[i] - l[key_char]) % 26
            c += rev[shifted_index]
            op += 1

    print(c)
    return c

while True:
    x=input()
    x.lower()
    f=input("enter the key")
    vdecode(x,f)
    

#rai;fence 
def rail_fence_encrypt(text, rails):
    # Create rails as empty lists
    fence = [[] for _ in range(rails)]
    rail = 0
    direction = 1  # 1 = down, -1 = up

    for char in text:
        fence[rail].append(char)
        rail += direction

        # Change direction at the top and bottom rails
        if rail == 0 or rail == rails - 1:
            direction *= -1

    # Flatten the fence by concatenating rails
    result = ''.join(''.join(row) for row in fence)
    return result

def rail_fence_decrypt(cipher, rails):
    # Prepare the fence with placeholders
    fence = [['\n' for _ in range(len(cipher))] for _ in range(rails)]

    # Mark the positions to fill
    rail = 0
    direction = 1
    for i in range(len(cipher)):
        fence[rail][i] = '*'
        rail += direction
        if rail == 0 or rail == rails -1:
            direction *= -1

    # Fill the fence with the cipher text
    index = 0
    for r in range(rails):
        for c in range(len(cipher)):
            if fence[r][c] == '*' and index < len(cipher):
                fence[r][c] = cipher[index]
                index += 1

    # Now read the fence in zigzag manner to get original text
    result = []
    rail = 0
    direction = 1
    for i in range(len(cipher)):
        result.append(fence[rail][i])
        rail += direction
        if rail == 0 or rail == rails - 1:
            direction *= -1

    return ''.join(result)


# Example usage:
plaintext = input('->')
rails = 3

encrypted = rail_fence_encrypt(plaintext.replace(" ", ""), rails)
print("Encrypted:", encrypted)

decrypted = rail_fence_decrypt(encrypted, rails)
print("Decrypted:", decrypted)
'''
#acrostic
def acrostic_lines(text):
    lines = text.strip().split('\n')
    result = ''

    for line in lines:
        line = line.strip()
        if not line:
            continue
        first_char = line[0].lower()
        if first_char.isalpha():  # only use lines that start with letters
            result += first_char
        else:
            result += first_char
            

    return result
x='''
Hold steady, for your journey deepens.  
Traverse the path of seekers and shadows.  
Trust only the clues that whisper truth.  
Perhaps the stars above still guide.  
Seek not chaos, but structure in disorder.  
:  
:  
gather your thoughts with care,  
in silence find the trail,  
to what lies hidden in the web.  
hints reside between the lines.  
each letter — a step ahead.  
.  
ciphers protect it well,  
obscure yet always fair.  
many overlook the obvious.  
/  
Find the fire that sparks the hunt.  
inquiry fuels the bold.  
next comes what you seek:  
daring to decipher the forgotten.  
-  
the veil is thin.  
hearken now.  
enter the wild...  
x marks the spot.  
tread lightly, but don’t delay.  
-  
hinted once, now made clear:  
3 digits guide the way.  
3 trials still remain.  
0 reasons to stop.  
2 paths to truth.  
/  
the echo leads you home.  
hurry, but do not stumble.  
enlightenment lies ahead.  
whispers call the worthy.  
intellect unlocks the hidden.  
never forget what brought you here.  
truth awaits.'''

# Run the loop
print("Encoded:", acrostic_lines(x))
