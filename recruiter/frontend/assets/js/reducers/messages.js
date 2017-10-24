import uuid from 'node-uuid';
import Immutable from 'immutable';
import { messageTypes }  from '../config.js';
import * as actionTypes from '../actions/action-types';

const messages = (state = new Immutable.Map().withMutations(ctx => ctx.set('activeChat', 0).set('messageList', new Immutable.List())), action) => {
    if (action.type === messageTypes.initChat) {
        let pendingMesssages = state.get('messageList').valueSeq().filter(x => x.has('pendingId'));
        let messagesFromServer = Immutable.fromJS(action.payload.messages);
        return new Immutable.Map().withMutations(ctx => {
            return ctx.set('activeChat', action.payload.conversation_id)
                .set('messageList', messagesFromServer.concat(pendingMesssages))
                .set('more', Immutable.fromJS(action.payload.more));
        });
    }
    if(action.type == actionTypes.ADD_PENDING_MESSAGE){
      action.payload.pendingId = 'pendingId-' + uuid.v4();
      action.payload.messagePendingSend.pendingId = action.payload.pendingId;
      const messageList = state.get('messageList').push(Immutable.fromJS(action.payload));
      return state.set('messageList', messageList);
    }
    if(action.type === messageTypes.newMessage){
      // Remove delivered message
      if(action.payload.pendingId){
        state = state.set(
          'messageList',
          state.get('messageList').filter(
            msg => msg.id == undefined && msg.get('pendingId') != action.payload.pendingId
          )
        );
        delete action.payload.pendingId;
      }
    }
    if (action.type === messageTypes.newMessage && action.payload.conversation_id === state.get('activeChat')) {
        // TODO: There may be an optimization here, consult Immutable.JS docs
        const messageList = state.get('messageList').push(Immutable.fromJS(action.payload));
        return state.set('messageList', messageList);
    }
    if (action.type === messageTypes.moreMessages && action.payload.conversation_id === state.get('activeChat')) {
        const messageList = Immutable.fromJS(action.payload.messages).concat(state.get('messageList'));
        return state.withMutations(ctx => {
            return ctx.set('messageList', messageList)
                .set('more', Immutable.fromJS(action.payload.more));
        });
    }
    if (action.type === messageTypes.answerInvite && action.payload.conversation_id === state.get('activeChat')) {
        return state.update('messageList', messageList => {
            return messageList.map(message => {
                if (message.get('group_invite') && message.get('group_invite').get('conversation_id') === action.payload.group_id) {
                    if (action.payload.accept && message.getIn(['group_invite', 'status']) === 1) {
                        return message.updateIn(['group_invite', 'status'], () => 0);
                    } else if (!action.payload.accept && message.getIn(['group_invite', 'invite_id']) === action.payload.invite_id) {
                        return message.updateIn(['group_invite', 'status'], () => 2);
                    } else return message;
                } else return message;
            });
        });
    }
    if (action.type === messageTypes.kickUser) {
        return state.update('messageList', messageList => {
            return messageList.filter(message => !message.get('group_invite') || message.get('group_invite').get('conversation_id') !== action.payload);
        });
    }
    return state;
};

export {
    messages
};
