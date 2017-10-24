import Immutable from 'immutable';

import * as config from '../config.js';


const { messageTypes } = config;

const users = (state = new Immutable.Map().set('self', 0), action) => {
    if (action.type === messageTypes.init) {
        return new Immutable.Map(Immutable.fromJS(action.payload.users));
    }
    if (action.type === messageTypes.userPresence) {
        return state.mergeDeep(action.payload);
    }
    if (action.type === messageTypes.userTyping) {
        if (state.has(action.payload.id.toString())) {
            return state.mergeIn([action.payload.id.toString()], {online: 2});
        } else return state;
    }
    if (action.type === messageTypes.newMessage) {
        if (state.has(action.payload.user.id.toString())) {
            return state.mergeIn([action.payload.user.id.toString()], {online: 2});
        } else return state;
    }
    if (action.type === messageTypes.createGroup) {
        const {extra} = action.payload;
        return state.mergeIn(['extra'], Immutable.fromJS(extra));
    }
    return state;
};

export {
    users
};
