from subprocess import Popen, PIPE


class Listener:
    def __init__(self, server_name="server.jar"):
        self.server = Popen(f"java -Xmx1024M -Xms1024M -jar {server_name} nogui",
                            stdin=PIPE, shell=True)

    def run_command(self, command):
        self.server.stdin.write(bytes(command + "\r\n", "ascii"))
        self.server.stdin.flush()
