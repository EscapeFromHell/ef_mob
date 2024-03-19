class Data:
    def __init__(self, data: str, destination_ip: int) -> None:
        self.data: str = data
        self.destination_ip: int = destination_ip


class Server:
    next_ip = 1

    def __init__(self) -> None:
        self.buffer = []
        self.ip = Server.next_ip
        Server.next_ip += 1

    def send_data(self, data_packet: Data) -> None:
        router.buffer.append(data_packet)

    def get_data(self) -> list[Data]:
        data_packets = self.buffer[:]
        self.buffer.clear()
        return data_packets

    def get_ip(self) -> int:
        return self.ip

    def receive_data(self, data_packet: Data) -> None:
        self.buffer.append(data_packet)


class Router:
    def __init__(self) -> None:
        self.connected_servers: list[Server] = []
        self.buffer: list[Data] = []

    def link(self, server: Server) -> None:
        self.connected_servers.append(server)

    def unlink(self, server: Server) -> None:
        if server in self.connected_servers:
            self.connected_servers.remove(server)

    def send_data(self) -> None:
        for data_packet in self.buffer:
            destination_ip = data_packet.destination_ip
            for server in self.connected_servers:
                if server.get_ip() == destination_ip:
                    server.receive_data(data_packet)
        self.buffer.clear()


router = Router()
sv_from = Server()
sv_from2 = Server()
router.link(sv_from)
router.link(sv_from2)
router.link(Server())
router.link(Server())
sv_to = Server()
router.link(sv_to)

sv_from.send_data(Data("Hello", sv_to.get_ip()))
sv_from.send_data(Data("Hello", sv_to.get_ip()))
sv_to.send_data(Data("Hi", sv_from.get_ip()))

router.send_data()

msg_lst_from = sv_from.get_data()
msg_lst_to = sv_to.get_data()

print([data.data for data in msg_lst_from])
print([data.data for data in msg_lst_to])
