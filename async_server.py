import asyncio, random
from Socket_Async import Socket


class Server(Socket):
	def __init__(self):
		super(Server, self).__init__()

		self.users = []
		self.usernames = {}

	def set_up(self):
		self.socket.bind(('127.0.0.1', 9090))
		self.socket.listen(55)
		self.socket.setblocking(False)
		print('server listening')

	async def send_data(self, data=None, listened_socket=None):
		name = self.usernames[listened_socket]
		msg = f"{name}: {data}"
		for user in self.users:
			await self.main_loop.sock_sendall(user, msg.encode())

	async def listen_socket(self, listened_socket=None):
		if listened_socket is None:
			return

		while True:
			data = await self.main_loop.sock_recv(listened_socket, 2048)
			print(f'user send {data}')
			await self.send_data(data, listened_socket)

	async def accept_sockets(self):
		while True:
			names = ['sasha', 'slavik', 'misha', 'ivan']
			user_socket, address = await self.main_loop.sock_accept(self.socket)
			print(f'User {address[0]} connected')
			self.usernames[user_socket] = names[random.randint(0, 3)]
			self.users.append(user_socket)
			self.main_loop.create_task(self.listen_socket(user_socket))

	async def main(self):
		await self.main_loop.create_task(self.accept_sockets())


if __name__ == '__main__':
	server = Server()
	server.set_up()
	print('запущенно')

	server.start()


