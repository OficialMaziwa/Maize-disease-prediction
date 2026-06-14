from werkzeug.security import generate_password_hash

password = "Malaba@22"
hash_value = generate_password_hash(password)
print(f"Password: {password}")
print(f"Hash: {hash_value}")
