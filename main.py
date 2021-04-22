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

    def get_command(self, command: str):
        return "/give Mihendy gold_block"  # test
        # return requests.get(self.end_point + "/command_id", params={"key": self.key, "command": command}).json()

    def run_commands(self):
        for command_id in self:
            command = self.get_command(command_id)
            if self.server:
                self.server.stdin.write(bytes(command + "\r\n", "ascii"))
                self.server.stdin.flush()

    def __iter__(self):
        return self

    def __next__(self):
        resp = 0
        code = NOT_MOD
        while code == NOT_MOD:
            resp = requests.get(self.end_point + "/mock_resolve", params={"key": self.key})
            code = resp.status_code
        if code != SUCCESS:
            return
        return resp.json()[1]


if __name__ == "__main__":
    listener = Listener(key="1341")
    listener.start()
