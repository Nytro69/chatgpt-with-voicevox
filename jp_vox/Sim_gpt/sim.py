import openai
import dotenv
import os
import sys
from jp_vox import speak_jp
import argparse
import threading
import time

def text_json(text):
    """
    When getting a prompt back from chatgpt will it send the response in a json format, 
    this function returns the content of the json variable aka what chatgpt said.
    """
    return text['choices'][0]['message']['content']

def separate(string: str) -> str:
    """"
    When you get a response from chatgpt will the text not have any newline/line break,
    this funtion adds a newline for every 80 characters (when a word is finished).
    """
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


# preperations for extra command-line-arguments.
parser = argparse.ArgumentParser()
parser.add_argument('-m', type=str) # m for modify gpt
args = parser.parse_args()

# opens the env file so that we can get the gpt key
dotenv.load_dotenv()

# api key for chatgpt
z = os.getenv("API_KEY")

# uses the openai library to set the api key
openai.api_key = z

# sets up the gpt modifyers, and the chat history for the ai you're talking to and the ai that generates options
if args.m == "y": # if you set -m to y you get to modify the options and talking ai
    chat_history = [{"role": "system",
                     "content": f"{input("Talking ai: ")}, answer max in 3 sentances, if you've talked about the same thing three times; change the subject"},
                    {"role": "user", "content": "hi"}]
    chat_history_options = [{"role": "system", "content": f"{input("Options ai: ")}, answer max in 2 sentances"}]
else:
    chat_history = [{"role": "system", "content": "you are a user of chat-gpt try asking popular questions and don't act like an assistant, answer max in 3 sentances, if you've talked about the same thing three times; change the subject"},
                    {"role": "user", "content": "hi"}]
    chat_history_options = [{"role": "system", "content": "answer max in 2 sentances"}]


def send(chat_history_=chat_history_options, role="Teenager"):
    """
    this function sends a request to chatgpt, and then returns the response
    """
    chat_history_.append({"role": "system", "content": f"talk/pose questions like {role}"})

    thing = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history_options
    )
    chat_history_.pop()
    thing = text_json(thing)
    return thing


while True:
    # the talking ai says something depending on the chat_history
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history
    )

    # gets text of the reponse
    response = text_json(response)

    # adds it to chat history
    chat_history_options.append({"role": "user", "content": response})

    # shows the response to the user
    print(f"\n{separate(f"{response}")}\n")

    # creates a new thread that excecutes the speak_jp function, the reason for the thread is that the program runs faster if I operate on multible cpu cores
    thread = threading.Thread(target=speak_jp, args=(response,))
    thread.start()


    # generates options to choose from
    one = send(chat_history_=chat_history_options, role="a Teenager")
    two = send(chat_history_=chat_history_options, role="your trying to change the subject")
    three = send(chat_history_=chat_history_options, role="ben shapiro")

    # makes versions of the options that have newlines in them for better readability
    one_s = separate(f"{one}")
    two_s = separate(f"{two}")
    three_s = separate(f"{three}")

    # waits for the speak_jp to finish
    thread.join()

    # the user chooses one of the options as a response to what the talking ai said or makes an answer of their own
    user = int(input(f"1: {one_s}\n\n2: {two_s}\n\n3: {three_s}\n\n4: Own Answer\n\nYour choice: ").strip())

    # checks what they choose for option
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

    # repeates
