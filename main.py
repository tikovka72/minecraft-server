from subprocess import Popen, PIPE
import requests
import argparse
import time

SUCCESS = 200
NOT_MOD = 304


class AuthError(Exception):
    ...


parser = argparse.ArgumentParser()
parser.add_argument("--need-java", default=0)
parser.add_argument("--end-point", default="http://127.0.0.1:4848")
parser.add_argument("--key", default="000")
args = parser.parse_args()
NEED_JAVA = args.need_java
END_POINT = args.end_pos
KEY = args.key


class Listener:
    def __init__(self, server_name="server.jar", end_point=END_POINT, key=None):
        if not key:
            raise AuthError
        self.key = key
        self.server = None
        if NEED_JAVA:
            self.server = Popen(f"java -Xmx1024M -Xms1024M -jar {server_name} nogui",
                                stdin=PIPE, shell=True)
        self.end_point = end_point

    def start(self):
        self.run_commands()

    @staticmethod
    def replace_user(command, user=None):
        if "<user>" in command:
            return command.replace("<user>", user or "@a")
        return command

    def get_command(self, command_id: str):
        # return "/give Mihendy gold_block"  # test
        r = requests.get(self.end_point + "/get_command",
                         params={"key": self.key, "command_id": command_id})
        if r.status_code != 200:
            return None
        return r.json()[1]

    def run_commands(self):
        for data in self:
            if data:
                pay_id, command_id = data
                command = self.get_command(command_id)
                command_with_user = self.replace_user(command)
                if self.server:
                    self.server.stdin.write(bytes(command_with_user + "\r\n", "ascii"))
                    self.server.stdin.flush()

    def __iter__(self):
        return self

    def __next__(self):
        resp = 0
        code = NOT_MOD
        while code == NOT_MOD:
            resp = requests.get(self.end_point + "/resolve", params={"key": self.key})
            code = resp.status_code
            time.sleep(0.5)
        if code != SUCCESS:
            return
        return resp.json()


if __name__ == "__main__":
    listener = Listener(key=KEY)
    listener.start()
