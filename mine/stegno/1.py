from matplotlib.image import imread
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
import numpy as np

p = 23


def steg_write(image_path, message, output_path='edited_image.png', spacing=10):
    if not image_path.lower().endswith('.png'):
        raise ValueError('The input image must be a PNG file')

    img = Image.open(image_path)
    pixel_array = np.array(img)

    message_values = [ord(char) for char in message]
    image_shape = pixel_array.shape

    pixel_list = pixel_array.flatten().tolist()
    if len(message_values) * spacing > len(pixel_list):
        raise ValueError('Message is too long for the given image and spacing')

    idx_list = [idx * spacing for idx in range(len(message_values))]

    for idx, char in zip(idx_list, message_values):
        pixel_list[idx] = char

    edited_array = np.array(pixel_list).reshape(image_shape).astype(np.uint8)
    edited_img = Image.fromarray(edited_array)
    edited_img.save(output_path)

    print(f'Message Length: {len(message)}')
    print('Image Saved!')

def steg_read(image_path, message_length, spacing=10):
    img = Image.open(image_path)
    pixel_array = np.array(img)
    pixel_list = pixel_array.flatten().tolist()

    idx_list = [idx * spacing for idx in range(message_length)]
    hidden_values = [pixel_list[idx] for idx in idx_list]
    chars = [chr(value) for value in hidden_values]

    return ''.join(chars)

# --- Encryption Function ---

def encr(message):
    x = message
    priv = int(input("Enter your private key: "))
    other_pub = int(input("Enter other party's public key: "))

    s = pow(other_pub, priv, p)
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
            en.append('-1')
        else:
            val = (ord(i) * factor)
            en.append(str(val))

    # Append markers
    en.append('009901' + str(mi * s))
    en.append('009900' + str(ma * s))

    encrypted_str = ' '.join(en)
    return encrypted_str

# --- Decryption Function ---

def decr(revealed, message_len):
    decrypted = ''
    ex1 = revealed
    priv2 = int(input("Enter your private key again: "))
    sender_pub = int(input("Enter sender's public key: "))

    s2 = pow(sender_pub, priv2, p)

    mi_str = ex1[-2]
    ma_str = ex1[-1]

    if not (mi_str.startswith('009901') and ma_str.startswith('009900')):
        raise ValueError("Invalid encryption format.")

    mi2 = int(mi_str[6:]) // s2
    ma2 = int(ma_str[6:]) // s2

    factor2 = ((mi2 * ma2) * s2)
    encrypted_values = ex1[:-2]

    for val in encrypted_values:
        if val == '-1':
            decrypted += ' '
        else:
            num = int(val)
            original_ord = num // factor2
            decrypted += chr(original_ord) if 0 <= original_ord <= 1114111 else '?'

    return decrypted


while True:
    op = int(input("\nEnter option (1 to hide, 2 to reveal, 0 to exit): "))
    if op == 1:
        original_msg = input("Enter your secret message: ")
        message = encr(original_msg)
        steg_write(
            r'C:\Users\bina1\OneDrive\Desktop\main\main\mine\stegno\dog_picture.png',
            message,
            output_path='edited_image.png',
            spacing=10
        )
        plt.imshow(mpimg.imread('edited_image.png'))
        plt.axis('off')
        plt.title("Image with Hidden Message")
        plt.show()

    elif op == 2:
        message_length = int(input("Enter the length of the hidden message: "))
        revealed = steg_read('edited_image.png', message_length, spacing=10)
        print("\nHidden message:", decr(revealed.split(), message_length))

    elif op == 0:
        print("Exiting...")
        break

    else:
        print("Invalid option. Try again.")
