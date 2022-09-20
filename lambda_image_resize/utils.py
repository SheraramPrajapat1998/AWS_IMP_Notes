
from base64 import b64decode
import os
import boto3

decrypted_hashmap = {}


def decrypt_secret(secret_name):
    if secret_name in decrypted_hashmap:
        print(f"Returning cached {secret_name}")
        return decrypted_hashmap[secret_name]
    print(f"Decrypting {secret_name}")
    try:
        ENCRYPTED = secret_name
        # Decrypt code should run once and variables stored outside of the function
        # handler so that these are decrypted once per container
        DECRYPTED = boto3.client('kms').decrypt(
            CiphertextBlob=b64decode(ENCRYPTED),
            EncryptionContext={'LambdaFunctionName': os.environ['AWS_LAMBDA_FUNCTION_NAME']})['Plaintext'].decode('utf-8')
        decrypted_hashmap[secret_name] = DECRYPTED
        return DECRYPTED
    except Exception as e:
        print(e)
