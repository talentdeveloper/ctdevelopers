import Immutable from 'immutable';

import * as config from '../config.js';
import * as actionTypes from '../actions/action-types.js';


const { messageTypes } = config;

const typing = (state = new Immutable.Map().withMutations(ctx => ctx.set('activeChat', 0).set('typingMap', new Immutable.Map())), action) => {
    if (action.type === messageTypes.userTyping && action.payload['conversation_id'] === state.get('activeChat')) {
        return state.setIn(
            ['typingMap', action.payload.id],
            Immutable.fromJS({
                user_name: action.payload.name,
                timer_id: 0
            })
        );
    }
    if (action.type === actionTypes.typeTimerStart) {
        return state.setIn(
            ['typingMap', action.payload.user_id],
            Immutable.fromJS({
                user_name: action.payload.user_name,
                timer_id: action.payload.timer_id
            })
        );
    }
    if (action.type === actionTypes.typeTimerExpire) {
        const value = state.get('typingMap').get(action.payload.user_id);
        if (value && value.get('timer_id') === action.payload.timer_id) {
            return state.deleteIn(['typingMap', action.payload.user_id]);
        } else {
            return state;
        }
    }
    if (action.type === messageTypes.initChat) {
        return new Immutable.Map().withMutations(ctx => ctx.set('activeChat', action.payload.conversation_id).set('typingMap', new Immutable.Map()));
    }
    if (action.type === messageTypes.newMessage && action.payload.conversation_id === state.get('activeChat')) {
        return state.deleteIn(['typingMap', action.payload.user.id]);
    }
    return state;
};

export {
    typing
};
