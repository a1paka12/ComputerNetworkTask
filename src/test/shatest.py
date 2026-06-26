import hashlib

text = "1234"
hash_object = hashlib.sha256(text.encode())
hex_dig = hash_object.hexdigest()
expected = "03ac674216f3e15c761ee1a5e255f067953623c8b388b4459e13f978d7c846f4";

print(hex_dig == expected)