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

    #     - Begin with a title page.
    # -Create a table of contents.
    # -Explain your “why” with an executive summary.
    # -State the problem or need.
    # -Propose a solution.
    # -Share your qualifications.
    # -Include pricing options.
    # -Summarize with a conclusion.
    # -Clarify your terms and conditions.

def connectGpt(prompt,template):
    message=[]
    if template!="NA":
        systemContent="""You are an assitant that helps to create business proposals.
        Use the below format for the proposals
        {temp}
        """.format(temp=template)
        print(systemContent)
        message.append({"role":"system","content":systemContent})
    message.append({"role": "user", "content": prompt})
    print(message)
    try:
        completion = openai.ChatCompletion.create(
        engine="bigaidea",
        messages=message
        )
        print(completion.choices)
        return completion.choices[0].message
    except Exception as e:
        print(e)
        return "0"



