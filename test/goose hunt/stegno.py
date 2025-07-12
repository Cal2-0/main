def steg_read(image_path, message_length, spacing=10):
    #open the image using PIL
    img = Image.open(image_path)
    pixel_array = np.array(img)

    pixel_list = pixel_array.flatten().tolist()

    #retrieve indices where the message will be hidden
    idx_list = [idx * spacing for idx in range(message_length)]

    #extract hidden message values
    hidden_values = [pixel_list[idx] for idx in idx_list]

    #convert ascii values to unicode
    chars = [chr(value) for value in hidden_values]

    return ''.join(chars)
steg_read(image_path='edited_image.png',message_length=5)