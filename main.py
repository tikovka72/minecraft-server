from subprocess import Popen, PIPE
import requests

SUCCESS = 200
NOT_MOD = 304


class AuthError(Exception):
    ...


class Listener:
    def __init__(self, server_name="server.jar", end_point="http://127.0.0.1:4545", key=None):
        need_java = 0
        if not key:
            raise AuthError
        self.key = key
        self.server = None
        if need_java:
            self.server = Popen(f"java -Xmx1024M -Xms1024M -jar {server_name} nogui",
                                stdin=PIPE, shell=True)
        self.end_point = end_point

    def start(self):
        self.run_commands()

    @staticmethod
    def replace_user(command, user):
        if "<user>" in command:
            return command.replace("<user>", user)
        return command

    def get_command(self, command_id: str):
        # return "/give Mihendy gold_block"  # test
        r = requests.get(self.end_point + "/get_command",
                         params={"key": self.key, "command_id": command_id})
        if r.status_code != 200:
            return None
        return r.json()["command"]

    def run_commands(self):
        for pay_id, command_id, username in self:
            command = self.get_command(command_id)
            command_with_user = self.replace_user(command, username)
            if self.server:
                self.server.stdin.write(bytes(command_with_user-+ + "\r\n", "ascii"))
                self.server.stdin.flush()

    def __iter__(self):
        return self

    def __next__(self):
        resp = 0
        code = NOT_MOD
        while code == NOT_MOD:
            resp = requests.get(self.end_point + "/resolve", params={"key": self.key})
            code = resp.status_code
        if code != SUCCESS:
            return
        return resp.json()


if __name__ == "__main__":
    listener = Listener(key="1341")
    listener.start()
