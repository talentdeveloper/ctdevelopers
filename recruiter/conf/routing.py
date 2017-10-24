from channels.routing import include

from chat.routing import routes as chat_routes

channel_routing = [
    include(chat_routes, path=r'^/chat')
]
