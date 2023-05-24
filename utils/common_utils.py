import jwt
import openai
import json

secret="third_eye_token"
key="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"
openai.organization = "org-1VpD8eXjrTWULhEFmwh1QIKG"
openai.api_key = key

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
    completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "create a business proposal layout"}
    ]
    )
    print(completion.choices[0].message.content)



