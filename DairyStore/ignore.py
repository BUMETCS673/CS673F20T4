# # Python program to explain os.environ object
#
# # importing os module
# import os
# import pprint
#
# # Get the list of user's
# # environment variables
# env_var = os.environ
#
# # Print the list of user's
# # environment variables
# print("User's Environment variable:")
# pprint.pprint(dict(env_var), width=1)

from crypto.Cipher import AES
import base64

cipher = AES.new("moodairyofficial", AES.MODE_ECB)
encode = base64.b64encode(cipher.encrypt("jycxld==3"))
decode = cipher.decrypt(base64.b64encode("jycxld==3"))
