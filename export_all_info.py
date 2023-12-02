#!/usr/bin/env python3.11

import os
import re
import time

import requests

from arrs_shell import get_connection_info, send_command

# USAGE: set credential file to a file containing lines of the form "username password" for all known users.
#   Then, run the script, and it will populate ../file_system (or custom dir) with all users' files/notes
#   Change custom parameters using CREDENTIAL_FILE=../credentials.txt FILESYSTEM=../file_system ./export_all_info.py

# Global variables
CREDENTIAL_FILE: str = os.getenv("CREDENTIAL_FILE", "../credentials.txt")
FILESYSTEM: str = os.getenv("FILESYSTEM", "../file_system")

php_sess_id, csrf_token = get_connection_info()
debug: bool = True
do_preprocessing: bool = False


def execute(cmd: str) -> list[str]:
    time.sleep(4)  # remove this if you like getting rate limited :)
    if debug:
        print(f"[DEBUG] Execute: {cmd}")

    working_response: requests.Response = send_command(
        f"{cmd}", csrf_token, php_sess_id
    )
    try:
        response = working_response.json()["message"].split("<br />")[1:]
    except requests.exceptions.JSONDecodeError:
        response = working_response.text.splitlines()

    if debug:
        print(f"[DEBUG] Respond: {response}")

    return response


def preprocess_line(line: str) -> str:
    if not do_preprocessing:
        return line

    new_line = re.sub(r"<.*?>", "\n", line)
    line2 = new_line.replace("&nbsp;", " ")
    half_fixed = line2.replace("&lt;", "<")
    fixed = half_fixed.replace("&gt;", ">")
    return fixed


def get_creds() -> list[tuple[str, str]]:
    creds: list[tuple[str, str]] = []
    if not os.path.exists(CREDENTIAL_FILE):
        print(f"Credential file {CREDENTIAL_FILE} not found.")
        exit(0)

    with open(CREDENTIAL_FILE, "r") as f:
        lines: list[str] = f.readlines()
        for line in lines:
            try:
                cred_user, cred_pass = line.strip("\n").split(" ")
                creds.append((cred_user, cred_pass))
            except ValueError:
                print(
                    f"Badly formatted line: {line}\nCheck spacings in the line. Continuing."
                )

    return creds


def make_directory_structure(username: str) -> bool:
    try:
        os.mkdir(f"{username}")
    except FileExistsError:
        return False

    os.chdir(f"{username}")
    directories = "files", "notes"
    for directory in directories:
        try:
            os.mkdir(f"{directory}")
        except FileExistsError:
            pass

    return True


def get_and_store_user_string() -> None:
    contents = execute("user")
    with open("user", "w+") as file:
        contents = list(map(preprocess_line, contents))
        file.write("\n".join(contents))


def get_directory_listing() -> list[str]:
    res = execute("dir")
    if len(res) == 1 and "no files found" in res[0]:
        return []

    return res


def create_files(filenames: list[str]) -> None:
    for filename in filenames:
        if not filename:  # if the filename is blank, don't create it
            continue

        with open(f"{filename}", "w+") as file:
            contents = execute(f"file {filename}")
            contents = list(map(preprocess_line, contents))
            file.write("\n".join(contents))


def get_notes_listing() -> list[str]:
    return execute("notes")


def create_notes(note_names: list[str]) -> None:
    for note_name in note_names:
        if not note_name or "no notes found" in note_name:
            continue

        if "/" in note_name:
            print(f"Skipping invalid note name {note_name}.")
            continue

        with open(f"{note_name}", "w+") as note:
            contents = execute(f"note {note_name}")
            contents = list(map(preprocess_line, contents))
            note.write("\n".join(contents))


def main():
    creds: list[tuple[str, str]] = get_creds()
    # make root directory
    try:
        os.mkdir(FILESYSTEM)
    except FileExistsError:
        pass

    os.chdir(FILESYSTEM)

    for cred_user, cred_pass in creds:
        print(f"Beginning pass on user {cred_user}")
        creation_success = make_directory_structure(cred_user)
        if not creation_success:
            print(
                f"Data already exists for {cred_user}. Delete the directory if incomplete."
            )
            continue

        execute("logout")
        execute(f"login {cred_user}")
        res = execute(f"{cred_pass}")
        if res and ("error" in res[0] or "ERROR" in res[0]):
            print(f"Auth failed on user {cred_user}")
            continue

        get_and_store_user_string()

        os.chdir("./files")
        create_files(get_directory_listing())

        os.chdir("../notes")
        create_notes(get_notes_listing())

        os.chdir("../../")


if __name__ == "__main__":
    main()
