import jwt
import openai
import json

openai.api_type = "azure"
openai.api_key = "32c8f6789c1649f588d42312a2d827d0"
openai.api_base = "https://bigaidea.openai.azure.com/"
openai.api_version = "2023-03-15-preview"

secret="third_eye_token"
# key="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"
# openai.organization = "org-1VpD8eXjrTWULhEFmwh1QIKG"
# openai.api_key = key

def create_jwt(id):
    payload={
        "id":id
    }
    token = jwt.encode(
    payload=payload,
    key=secret
    )
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, key=secret, algorithms=['HS256', ])
        return True
    except Exception as e:
        return False

def get_id(token):
    try:
        payload = jwt.decode(token, key=secret, algorithms=['HS256', ])
        return payload['id']
    except Exception as e:
        return 0

def connectGpt(prompt):
    try:
        completion = openai.ChatCompletion.create(
        engine="bigaidea",
        messages=[
            {"role": "user", "content": prompt}
        ]
        )
        # print(completion.choices)
        return completion.choices[0].message
    except Exception as e:
        return "0"



