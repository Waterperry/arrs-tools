#!/usr/bin/env python3.11

import os
from sys import exit
import time

import requests


def get_connection_info() -> tuple[dict[str, str], str]:
    initial_response: requests.Response = requests.get("https://arrs.host/")
    php_sess_dict: dict[str, str] = dict(initial_response.cookies)
    csrf_token = [x for x in initial_response.content.decode().split("\n")
                  if "value" in x][0].split("\"")[7]
    return php_sess_dict, csrf_token


def send_command(
        command: str,
        csrf_token: str,
        php_sess_id: dict[str, str]
) -> requests.Response:
    response: requests.Response = requests.post(
            "https://arrs.host/ajax.php",
            cookies=php_sess_id,
            data={
                "token": csrf_token,
                "q": command.strip("\n"),
                "act": "command",
                },
            )
    return response


def get_and_preprocess_input() -> str | None:
    try:
        cmd: str = input("ARRS > ")
    except KeyboardInterrupt:
        print("\nExiting.")
        exit(0)
    if cmd == "clear":
        _ = os.system("clear")
        return None
    return cmd


def main():
    php_sess_id, csrf_token = get_connection_info()

    while True:
        time.sleep(4)  # Remove this if you like getting ARRS rate limited!
        cmd: str | None = get_and_preprocess_input()
        if cmd is None:
            continue

        arrs_res: requests.Response = send_command(cmd, csrf_token, php_sess_id)

        try:  # try to convert it to json and slap a newline at each breakpoint
            print("\n".join(arrs_res.json()["message"].split("<br />")[1:]))
        except requests.exceptions.JSONDecodeError:
            print(arrs_res.text)


if __name__ == "__main__":
    main()
