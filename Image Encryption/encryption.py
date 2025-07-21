from PIL import Image
import numpy as np
import random

def xor_encrypt(pixels, key):
    key_bytes = bytearray(key.encode())
    for i in range(pixels.shape[0]):
        for j in range(pixels.shape[1]):
            for k in range(3):  # R, G, B
                pixels[i, j, k] ^= key_bytes[(i + j + k) % len(key_bytes)]
    return pixels

def add_encrypt(pixels, key):
    key_bytes = bytearray(key.encode())
    for i in range(pixels.shape[0]):
        for j in range(pixels.shape[1]):
            for k in range(3):
                pixels[i, j, k] = (int(pixels[i, j, k]) + key_bytes[(i + j + k) % len(key_bytes)]) % 256
    return pixels

def shift_encrypt(pixels, key):
    key_shift = sum(bytearray(key.encode())) % 3  # shift by 0,1,2 (RGB)
    return np.roll(pixels, shift=key_shift, axis=2)

def shuffle_pixels(pixels, key):
    h, w, c = pixels.shape
    flat_pixels = pixels.reshape(-1, 3)
    rng = random.Random(sum(bytearray(key.encode())))
    indices = list(range(len(flat_pixels)))
    rng.shuffle(indices)
    shuffled = flat_pixels[indices]
    return shuffled.reshape(h, w, 3)

def encrypt_image(input_path, output_path, key, method):
    img = Image.open(input_path).convert("RGB")
    pixels = np.array(img).astype(np.uint8)  # ensure uint8 type

    if method == "xor":
        pixels = xor_encrypt(pixels.copy(), key)
    elif method == "add":
        pixels = add_encrypt(pixels.copy(), key)
    elif method == "shift":
        pixels = shift_encrypt(pixels.copy(), key)
    elif method == "combined":
        pixels = xor_encrypt(pixels.copy(), key)
        pixels = shuffle_pixels(pixels, key)
    else:
        raise ValueError("Unsupported encryption method.")

    encrypted_image = Image.fromarray(pixels.astype(np.uint8))
    encrypted_image.save(output_path)


def decrypt_image(input_path, output_path, key, method):
    img = Image.open(input_path)
    img = img.convert("RGB")
    pixels = np.array(img)

    if method == "xor":
        pixels = xor_encrypt(pixels, key)  # XOR is symmetric
    elif method == "add":
        key_bytes = bytearray(key.encode())
        for i in range(pixels.shape[0]):
            for j in range(pixels.shape[1]):
                for k in range(3):
                    pixels[i][j][k] = (pixels[i][j][k] - key_bytes[(i + j + k) % len(key_bytes)]) % 256
    elif method == "shift":
        key_shift = sum(bytearray(key.encode())) % 3
        pixels = np.roll(pixels, shift=-key_shift, axis=2)  # Reverse shift
    elif method == "combined":
        pixels = shuffle_pixels(pixels, key, reverse=True)
        pixels = xor_encrypt(pixels, key)
    else:
        raise ValueError("Unsupported decryption method.")

    decrypted_image = Image.fromarray(pixels.astype('uint8'))
    decrypted_image.save(output_path)

# Update shuffle_pixels to support reverse
def shuffle_pixels(pixels, key, reverse=False):
    h, w, c = pixels.shape
    flat_pixels = pixels.reshape(-1, 3)
    rng = random.Random(sum(bytearray(key.encode())))
    indices = list(range(len(flat_pixels)))
    rng.shuffle(indices)

    if reverse:
        # Rebuild original by inverting shuffle
        reverse_indices = [0] * len(indices)
        for i, idx in enumerate(indices):
            reverse_indices[idx] = i
        flat_pixels = flat_pixels[reverse_indices]
    else:
        flat_pixels = flat_pixels[indices]

    return flat_pixels.reshape(h, w, 3)
