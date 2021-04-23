from subprocess import Popen, PIPE
import requests
import argparse
import time
import json
import os

SUCCESS = 200
NOT_MOD = 304

LOG_LINE = "of a max of 20 players online:"


class AuthError(Exception):
    ...


parser = argparse.ArgumentParser()
parser.add_argument("--need-java", default=0)
parser.add_argument("--end-point", default="http://167.172.46.121:4545/")
parser.add_argument("--key", default="000")
args = parser.parse_args()
NEED_JAVA = args.need_java
END_POINT = args.end_point
KEY = args.key
join_text = " joined the game"
leave_text = " left the game"


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
        self.players = []
        self.last_log_size = 0
        self.last_log = ""

    def start(self):
        self.run_commands()

    def get_players_list(self):
        if os.path.getsize("logs/latest.log") != self.last_log_size:
            with open("logs/latest.log") as lo:
                logs = lo.read()
                self.last_log_size = os.path.getsize("logs/latest.log")
                logs = logs[logs.find(self.last_log) + len(self.last_log):]
                log_ = ""
                for log in logs.split("\n"):
                    log_ = log
                    if join_text in log:
                        player = log[log.find("]: ") + 3:log.find(join_text)]
                        if player not in self.players:
                            self.players.append(player)
                    elif leave_text in log:
                        player = log[log.find("]: ") + 3:log.find(leave_text)]
                        if player in self.players:
                            self.players.remove(player)
                self.last_log = log_
        return self.players

    @staticmethod
    def replace_user(command, user=None):
        if "<user>" in command:
            return command.replace("<user>", user or "@a")
        return command

    def get_command(self, command_id: str):
        # return "/give Mihendy gold_block"  # test
        r = requests.get(self.end_point + "/get_command",
                         params={"key": self.key, "command_id": command_id})
        if r.status_code != SUCCESS:
            return None
        return r.json()[1]

    def run_commands(self):
        for data in self:
            if data:
                pay_id, command_id, user = data
                command = self.get_command(command_id)
                command_with_user = self.replace_user(command, user)
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
            requests.post(self.end_point + "/announce_players_list",
                          data={"list": json.dumps(self.get_players_list()), "key": self.key})
        if code != SUCCESS:
            return
        try:
            return resp.json()
        except json.decoder.JSONDecodeError:
            return


if __name__ == "__main__":
    listener = Listener(key=KEY)
    listener.start()
