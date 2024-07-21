# import pkg_resources

# def is_installed(package):
#     try:
#         pkg_resources.get_distribution(package)
#         return True
#     except pkg_resources.DistributionNotFound:
#         return False

# packages = ["jose[cryptography]", "passlib[bcrypt]", "python-multipart"]

# for package in packages:
#     if is_installed(package):
#         print(f"Le package {package} est installé.")
#     else:
#         print(f"Le package {package} n'est pas installé.")


# import secrets

# # Générer une clé secrète de 256 bits
# secret_key = secrets.token_hex(32)

# print(secret_key)

# import bcrypt

# # def check_password(password, hashed_password):
# #     # Vérifier si le mot de passe correspond au hachage
# #     return bcrypt.checkpw(password.encode(), hashed_password.encode())

# # print("result is " + str(check_password(password, hashed_password)))

# def hash_password(password):
#     # Générer un sel
#     salt = bcrypt.gensalt()
#     # Hacher le mot de passe avec le sel
#     hashed_password = bcrypt.hashpw(password.encode(), salt)
#     return hashed_password.decode() 

# hashed_password = hash_password("arnaud")
# print(hashed_password)

import base64

def encode_base64(str_variable):
    str_variable_bytes = str_variable.encode('utf-8')
    str_variable_base64 = base64.b64encode(str_variable_bytes)
    return str_variable_base64.decode('utf-8')

def decode_base64(str_variable_base64):
    str_variable_base64_bytes = str_variable_base64.encode('utf-8')
    str_variable_bytes = base64.b64decode(str_variable_base64_bytes)
    return str_variable_bytes.decode('utf-8')

print(encode_base64('arnaud'))
print(decode_base64('YXJuYXVk'))
