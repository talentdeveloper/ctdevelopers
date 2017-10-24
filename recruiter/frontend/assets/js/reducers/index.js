import { combineReducers } from 'redux-immutable'

import { messages } from './messages.js';
import { typing } from './typing.js';
import { users } from './users.js';
import { chats } from './chats.js';

export default combineReducers({
    messages,
    typing,
    users,
    chats
});
