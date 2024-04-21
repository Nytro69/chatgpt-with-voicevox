import openai
import dotenv
import os
import sys
from jp_vox import speak_jp
import argparse
import threading
import time

def text_json(text):
    return text['choices'][0]['message']['content']

def separate(string: str) -> str:
    i = 0
    h = 0
    new = []
    while i < len(string):
        if i % 80 == 0 and i != 0:
            h = 1

        if string[i].isspace() and h == 1:
            new.append("\n")
            h = 0
            i += 1
            continue
        else:
            new.append(string[i])
            i += 1

    return ''.join(new)

parser = argparse.ArgumentParser()

parser.add_argument('-m', type=str)
args = parser.parse_args()

dotenv.load_dotenv()


z = os.getenv("API_KEY")

openai.api_key = z
if args.m == "y":
    chat_history = [{"role": "system",
                     "content": f"{input("Talking ai: ")}, answer max in 3 sentances, if you've talked about the same thing three times; change the subject"},
                    {"role": "user", "content": "hi"}]
    chat_history_options = [{"role": "system", "content": f"{input("Options ai: ")}, answer max in 2 sentances"}]
else:
    chat_history = [{"role": "system", "content": "you are a user of chat-gpt try asking popular questions and don't act like an assistant, answer max in 3 sentances, if you've talked about the same thing three times; change the subject"},
                    {"role": "user", "content": "hi"}]
    chat_history_options = [{"role": "system", "content": "answer max in 2 sentances"}]

def send(chat_history_=chat_history_options, role="Teenager"):
    chat_history_.append({"role": "system", "content": f"talk/pose questions like {role}"})

    thing = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history_options
    )
    chat_history_.pop()
    thing = text_json(thing)
    return thing


while True:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )

    response = text_json(response)

    chat_history_options.append({"role": "user", "content": response})


    print(f"\n{separate(f"{response}")}\n")

    thread = threading.Thread(target=speak_jp, args=(response,))

    thread.start()

    one = send(chat_history_=chat_history_options, role="a Teenager")
    two = send(chat_history_=chat_history_options, role="your trying to change the subject")
    three = send(chat_history_=chat_history_options, role="ben shapiro")

    one_s = separate(f"{one}")
    two_s = separate(f"{two}")
    three_s = separate(f"{three}")

    thread.join()

    user = int(input(f"1: {one_s}\n\n2: {two_s}\n\n3: {three_s}\n\n4: Own Answer\n\nYour choice: ").strip())


    if user == 1:
        chat_history.append({"role": "user", "content": one})
    elif user == 2:
        chat_history.append({"role": "user", "content": two})
    elif user == 3:
        chat_history.append({"role": "user", "content": three})
    elif user == 4:
        chat_history.append({"role": "user", "content": input("Answer: ").strip()})
    else:
        sys.exit("Invalid int")