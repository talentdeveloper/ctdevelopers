import Immutable from 'immutable';
import * as actionTypes from '../actions/action-types';
import { messageTypes } from '../config.js';


function sortChatsMap(map) {
    ['candidates', 'agents', 'groups',].forEach(group => {
        map = map.update(group, conversations => {
            return conversations.sortBy(conversation => new Date(conversation.get('last_message_time')), (a, b) => a === b ? 0 : (a > b ? -1 : 1));
        });
    });
    return map;
}

const initialState = Immutable.Map({
  socketIsConnected: null,
  chatInitialized: null,
  activeChat: 0,
  userSelfId: null,
  agents: Immutable.OrderedMap(),
  candidates: Immutable.OrderedMap(),
  groups: Immutable.OrderedMap(),
  supports: Immutable.OrderedMap(),
});

function chats(state=initialState, action){
    let prevState = state;
    if(action.type == actionTypes.SOCKET_CONNECTED){
        return state.set('socketIsConnected', true);
    }
    if(action.type == actionTypes.SOCKET_DISCONNECTED){
        return state.set('socketIsConnected', false).set('chatInitialized', false);
    }
    if(action.type == actionTypes.SOCKET_RECONNECTED){
        return state.set('socketIsConnected', true);
    }
    if (action.type === messageTypes.init) {
        return sortChatsMap(Immutable.Map(Immutable.fromJS(action.payload.chats)))
        .set('socketIsConnected', prevState.get('socketIsConnected'))
        .set('userSelfId', action.payload.users.self)
        .set('chatInitialized', false);
    }
    if (action.type === messageTypes.initChat) {
        // set unread messages to 0 when chat is open
        ['candidates', 'agents', 'groups'].forEach(group => {
            if (state.get(group).has(action.payload.conversation_id.toString())) {
                state = state.mergeIn(
                    [group, action.payload.conversation_id.toString()],
                    {
                        unread: 0
                    }
                )
            }
        })

        return state.set('activeChat', action.payload.conversation_id)
            .set('socketIsConnected', prevState.get('socketIsConnected'))
            .set('chatInitialized', true);
    }
    if (action.type === messageTypes.newMessage) {
        if (action.payload.user.id !== state.get('userSelfId') && action.payload.conversation_id !== state.get('activeChat')) {
            ['candidates', 'agents', 'groups'].forEach(group => {
                if (state.get(group).has(action.payload.conversation_id.toString())) {
                    state = sortChatsMap(state.mergeIn(
                        [group, action.payload.conversation_id.toString()],
                        {
                            unread: state.getIn([group, action.payload.conversation_id.toString(), 'unread']) + 1
                        }
                    ));
                }
            });
        }

        ['candidates', 'agents', 'groups'].forEach(group => {
            if (state.get(group).has(action.payload.conversation_id.toString())) {
                state = sortChatsMap(state.mergeIn(
                    [group, action.payload.conversation_id.toString()],
                    {
                        last_message_text: (action.payload.user.id === state.get('self') ? 'You: ' : `${action.payload.user.name}: `) + action.payload.text,
                        last_message_time: action.payload.time
                    }
                ));
            }
        });
    }
    if (action.type === messageTypes.readMessage) {
        if (state.get('agents').has(action.payload.toString())) {
            return state.mergeIn(['agents', action.payload.toString()], {unread: 0});
        } else if (state.get('candidates').has(action.payload.toString())) {
            return state.mergeIn(['candidates', action.payload.toString()], {unread: 0});
        } else if (state.get('groups').has(action.payload.toString())) {
            return state.mergeIn(['groups', action.payload.toString()], {unread: 0});
        } else return state;
    }
    if (action.type === messageTypes.createGroup) {
        const {id, extra, ...payload} = action.payload;
        return sortChatsMap(state.setIn(['groups', id.toString()], Immutable.fromJS(payload)));
    }
    if (action.type === messageTypes.leaveGroup) {
        return sortChatsMap(state.deleteIn(['groups', action.payload.toString()]));
    }
    if (action.type === messageTypes.chatsUpdate) {
        return sortChatsMap(state.setIn(['groups', action.payload.id.toString()], Immutable.fromJS(action.payload.data)));
    }
    return state;
};

export {
    chats
};
