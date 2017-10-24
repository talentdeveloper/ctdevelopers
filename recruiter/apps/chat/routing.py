from channels.routing import route_class

from chat.consumers import ChatServer

routes = [
    route_class(ChatServer, path=r'^/$'),
    route_class(ChatServer, path=r'^/(?P<mode>bg)?$'),
    route_class(ChatServer, path=r'^/(?P<cid>\d+)$')
]
