import * as actions from 'actions';
import {messageTypes, uri} from '../config.js';
import { postReceive } from './index.js';

class ChatSocket {
    constructor() {
        this.listenMap = new Map();
        this.attempts = 1;
    }

    emit(type, payload) {
        if (this.websocket.readyState == 1) {
            this.websocket.send(JSON.stringify({type, payload}));
        } else {
            console.error('Try to send when socket is not readyState', {type, payload});
        }
    }

    on(type, callback) {
        this.listenMap.set(type, callback);
    }

    createWebSocket(that, store) {
        this.websocket = new WebSocket(uri);

        this.websocket.onopen = () => {
            that.attempts = 1;
            if(store.getState().get('chats').get('socketIsConnected') == false){
                store.dispatch(actions.socketReconnected({attempts: this.attempts}))
            }else{
                store.dispatch(actions.socketConnected({attempts: this.attempts}))
            }
        };

        this.websocket.onmessage = event => {
            const data = JSON.parse(event.data);
            const callback = that.listenMap.get(data.type);
            if (callback) {
                callback(data.payload);
            }
        };

        function generateInterval (k) {
            return Math.min(30, (Math.pow(2, k) - 1)) * 1000;
        }
        this.websocket.onclose = () => { // TODO: stop reconnecting attempts on legit server decline.
            if(store.getState().get('chats').get('socketIsConnected')){
                store.dispatch(actions.socketDisconnected({attempts: that.attempts}));
            }
            const time = generateInterval(that.attempts);

            setTimeout(() => {
                // We've tried to reconnect so increment the attempts by 1
                that.attempts++;

                // Connection has closed so try to reconnect every 10 seconds.
                that.createWebSocket(that, store);
            }, time);
        }
    }
}

const socket = new ChatSocket();
window.socket = socket;

const init = (store) => {
    // add listeners to socket messages so we can re-dispatch them as actions
    socket.createWebSocket(socket, store);
    Object.keys(messageTypes)
        .forEach(type => socket.on(type, (payload) => {
            store.dispatch(postReceive({type, payload}));
            return store.dispatch({type, payload});
        }));
};

const emit = (type, payload) => socket.emit(type, payload);

export {
    init,
    emit
};
