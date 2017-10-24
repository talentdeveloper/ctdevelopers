import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Scrollbars } from 'react-custom-scrollbars';
import moment from 'moment';
import { Loader } from 'react-loaders';
import shallowEqual from 'shallowequal';
import { Map } from 'immutable';

import * as actions from 'actions';
import Message from './Message';


class MessageList extends React.Component {
    state = {
        prevScrollHeight: 0,
        pendingMore: false
    }

    scrollList(value) {
        this.scroll.scrollTop(value);
    }

    componentDidUpdate(prevProps, prevState) { // This is keeping scroll in place on requesting more messages.
        if (!this.scroll) {
            return;
        }
        if (prevProps.messages.get('messageList').size !== 0 && (this.props.messages.get('messageList').size - prevProps.messages.get('messageList').size > 1)) {
            this.scrollList(this.scroll.getScrollHeight() - this.state.prevScrollHeight);
        }
    }

    shouldComponentUpdate(nextProps, nextState) {
        if(this.getActiveChat() == null){
            return false;
        }
        return !shallowEqual(this.state, nextState) || !shallowEqual(this.props, nextProps);
    };

    componentWillReceiveProps(nextProps) {
        const { messages } = nextProps;
        const { actions } = this.props;

        // Send messages, which was be posted at offline
        if(this.props.chats.get('chatInitialized') == false && nextProps.chats.get('chatInitialized') == true){
            this.props.messages.get('messageList').valueSeq().forEach(function(message){
                if(message.get('pendingId') && message.get('conversation_id') == messages.get('activeChat')){
                    actions.resendMessage(message.get('messagePendingSend').toJS());
                }
            })
        }

        if (messages.get('more') === this.props.messages.get('more') && messages.get('messageList').size - this.props.messages.get('messageList').size === 1) { // One new message came
            let messageId = messages.get('messageList').last().get('id');
            if(messageId){
                this.props.actions.readMessage(messageId);
            }
            setTimeout(() => this.scrollList(this.scroll.getScrollHeight()), 10);
        }
        if (this.props.messages.get('activeChat') !== messages.get('activeChat')) { // Chat init happened
            this.props.setChatInitPendingState(false);
            setTimeout(() => this.scrollList(this.scroll.getScrollHeight()), 10);
        }
        if (this.props.messages.get('activeChat') === messages.get('activeChat')
            && (messages.get('messageList').size - this.props.messages.get('messageList').size > 1
                || (messages.get('messageList').size - this.props.messages.get('messageList').size === 1
                && messages.get('more') !== this.props.messages.get('more')))) { // More messages loaded
            this.setState({pendingMore: false});
        }
    }

    formatDate(date) {
        const now = moment();
        const then = moment(date);
        if (then.isSame(now, 'day')) {
            return 'Today';
        } else if (then.isSame(now.subtract(1, 'days'), 'day')) {
            return 'Yesterday';
        } else if (then.isBetween(now.subtract(5, 'days'), now, 'day')) {
            return then.format('dddd');
        } else {
            return then.format('dddd, MMMM Do, YYYY');
        }
    }

    moreMessages = first_message_id => () => {
        this.setState({
            prevScrollHeight: this.scroll.getScrollHeight(),
            pendingMore: true
        });
        this.props.actions.moreMessages(first_message_id);
    }

    renderMoreMessagesButton(messages) {
        if (this.state.pendingMore) {
            return <Loader type='ball-pulse' active />
        } else if (messages.get('more')) {
            return <button className='message-list-more' onClick={this.moreMessages(messages.get('messageList').get(0).get('id'))}>More</button>;
        } else {
            return <div />;
        }
    }

    acceptInvite = (conversation_id, invite_id) => {
        this.props.actions.answerInvite({accept: true, conversation_id, invite_id});
    }

    declineInvite = (conversation_id, invite_id) => {
        this.props.actions.answerInvite({accept: false, conversation_id, invite_id});
    }

    getActiveChat(){
        const { chats } = this.props;
        let chat = null;
        ['candidates', 'agents', 'groups'].some(group => {
            if (chats.get(group).has(chats.get('activeChat').toString())) {
              chat = chats.get(group).get(chats.get('activeChat').toString());
              return true;
            } else return false;
        });
        return chat;
    }
    render() {
        const { messages, users, chats, chatInitPending } = this.props;

        if (chatInitPending) {
            return (
                <div className='message-list-container'>
                    <Loader type='ball-pulse' active />
                </div>
            );
        }

        let chat = this.getActiveChat() || Map();

        const moreMessagesButtonUI = this.renderMoreMessagesButton(messages);
        return (
            <div className='message-list-container'>
                <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                            style={{height: '100%'}}
                            autoHide autoHideTimeout={1000}
                            autoHideDuration={200}>
                    <div className='message-list'>
                        {moreMessagesButtonUI}
                        {messages.get('messageList').map((message, index) => {
                            let dateUI = '';
                            if (index === 0 || !moment(message.get('time')).isSame(moment(messages.get('messageList').get(index-1).get('time')), 'day')) {
                                dateUI = <div className='message-list-date'>{this.formatDate(message.get('time'))}</div>
                            }
                            return (
                                <div key={index}>
                                    {dateUI}
                                    <Message
                                        user={chat.get('user') || users.has(message.get('user').get('id').toString()) ?
                                            users.get(message.get('user').get('id').toString()) :
                                            users.get('extra').get(message.get('user').get('id').toString())
                                        }
                                        text={message.get('text')}
                                        time={message.get('time')}
                                        group_invite={message.get('group_invite')}
                                        onAccept={this.acceptInvite}
                                        onDecline={this.declineInvite}
                                        pendingId={message.get('pendingId')}
                                        activeChat={chats.get('activeChat')}
                                        attachments={message.get('attachments')}
                                    />
                                </div>
                            );
                        }).toArray()}
                    </div>
                </Scrollbars>
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        users: state.get('users'),
        chats: state.get('chats'),
        messages: state.get('messages')
    };
}

function mapDispatchToProps (dispatch) {
    return {
        actions: bindActionCreators(actions, dispatch)
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(MessageList);
