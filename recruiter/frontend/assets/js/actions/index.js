import moment from 'moment';
import { List } from 'immutable';

import { messageTypes } from '../config';
import * as actionTypes from './action-types';


export function sendMessage(payload) {
    return (dispatch, getState, {emit}) => {
        let action = dispatch(addPendingMessage(getState(), payload));
        if(window.socket.websocket.readyState == 1){
            emit(messageTypes.newMessage, action.payload.messagePendingSend);
        }
    };
}

export function resendMessage(payload){
    return (dispatch, getState, {emit}) => {
        if(window.socket.websocket.readyState == 1){
            emit(messageTypes.newMessage, payload);
        }
    }
}

export function resendAllPendingMessages(){
    return (dispatch, getState, {emit}) => {
        if(window.socket.websocket.readyState != 1) return;
        let state = getState();
        state.get('messages').get('messageList').valueSeq().forEach(function(message){
            if(message.get('pendingId') && message.get('conversation_id')){
                if(window.socket.websocket.readyState == 1){
                    emit(messageTypes.newMessage, message.get('messagePendingSend').toJS());
                }
            }
        });
    }
}

export function addPendingMessage(state, payload) {
    const pending_payload = {
        'user': {
            'id': state.get('users').get('self'),
            'name': state.get('users').get('' + state.get('users').get('self')).get('name')
        },
        'group_invite': null,
        'text': payload.message,
        'messagePendingSend': payload,
        'attachments': {
        'files': List(payload.attachment.files),
        'file_names': List(payload.attachment.file_names),
        'file_sizes': List(payload.attachment.file_sizes)
        },
        'conversation_id': payload.conversation_id,
        'time': moment().utc().format('YYYY-MM-DDTHH:mm:ss.ms+00:00'),
    };

    return {
        type: actionTypes.ADD_PENDING_MESSAGE,
        payload: pending_payload
    };
}

export function userTyping() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userTyping, {});
    }
}

export function userPresence() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userPresence, {});
    }
}

export function typeTimerStart(payload) {
    return {type: actionTypes.typeTimerStart, payload}
}

export function typeTimerExpire(payload) {
    return {type: actionTypes.typeTimerExpire, payload}
}

export function initChat(conversation_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.initChat, conversation_id);
    }
}

export function moreMessages(message_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.moreMessages, {message_id});
    }
}

export function userIdle(idle) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.userIdle, idle);
    }
}

export function readMessage(message_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.readMessage, message_id); // TODO: refactor other actions like this.
    }
}

export function createGroup(payload) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.createGroup, payload);
    }
}

export function answerInvite(payload) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.answerInvite, payload);
    }
}

export function leaveGroup() {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.leaveGroup, {});
    }
}

export function kickUser(user_id) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.kickUser, user_id);
    }
}

export function inviteUsers(payload) {
    return (dispatch, getState, {emit}) => {
        emit(messageTypes.inviteUsers, payload);
    }
}

export function postReceive(data) {
    return (dispatch, getState, {emit}) => {
        const {type, payload} = data;
        if (type === messageTypes.leaveGroup && getState().get('chats').get('activeChat') === payload) {
            emit(messageTypes.initChat, null);
        }
    }
}

export function socketConnected(payload){
    return {
        type: actionTypes.SOCKET_CONNECTED,
        payload
    }
}

export function socketDisconnected(payload){
    return {
        type: actionTypes.SOCKET_DISCONNECTED,
        payload
    }
}

export function socketReconnected(payload){
    return {
        type: actionTypes.SOCKET_RECONNECTED,
        payload
    }
}
