import os

def check(channel:str, username:str) -> str:
    command = f"python3 grabber/grabber.py {channel} {username}"
    answ = os.popen(command).read()
    answ = answ.replace('\n', '')
    return answ

