import hashlib

password = "4567"
hashed_password = hashlib.sha256(password.encode()).hexdigest()
print('ХЭШ', hashed_password)