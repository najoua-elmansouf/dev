import openai
openai.api_key = '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'
messages=[{"role":"system","content":"you are a kind helpful assistant"},]
while True:
    message = input("User : ")
    if message:
        messages.append({"role":"user","content":message},)
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=messages)
    reply = chat.choices[0].message.content
    print(f"chatGPT:{reply}")
    messages.append({"role":"assistant","content":reply})
