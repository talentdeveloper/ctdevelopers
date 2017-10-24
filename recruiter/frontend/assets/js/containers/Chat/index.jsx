import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';

import * as actions from 'actions';
import UserList from 'components/UserList';
import MessageList from 'components/MessageList';
import MessageForm from 'components/MessageForm';
import TypingList from 'components/TypingList';
import CreateGroupChatModal from 'components/ChatModals/GroupChatModal';
import LeaveGroupChatModal from 'components/ChatModals/LeaveChatModal';
import InfoGroupChatModal from 'components/ChatModals/InfoGroupModal';
import ChatHeader from 'components/ChatHeader';
import IssueMonitor from 'components/IssueMonitor';

import '../../../css/chat.scss';


class App extends React.Component {
    state = {
        chatInitPending: false,
        showCreateGroupChatModal: false,
        showLeaveGroupChatModal: false,
        showInfoGroupChatModal: false
    }

    setChatInitPendingState = (state) => {
        this.setState({chatInitPending: state});
    }

    handleOpenCreateGroupChatModal = () => {
        this.setState({showCreateGroupChatModal: true});
    }

    handleCloseCreateGroupChatModal = () => {
        this.setState({showCreateGroupChatModal: false});
    }

    handleOpenLeaveGroupChatModal = () => {
        this.setState({showLeaveGroupChatModal: true});
    }

    handleCloseLeaveGroupChatModal = () => {
        this.setState({showLeaveGroupChatModal: false});
    }

    handleOpenInfoGroupChatModal = () => {
        this.setState({showInfoGroupChatModal: true});
    }

    handleCloseInfoGroupChatModal = () => {
        this.setState({showInfoGroupChatModal: false});
    }

    handleCreateGroup = (user_ids, name, message) => {
        this.props.actions.createGroup({user_ids, name, message});
        this.setState({showCreateGroupChatModal: false});
    }

    handleLeaveGroup = () => {
        this.props.actions.leaveGroup();
        this.setState({showLeaveGroupChatModal: false});
    }

    handleKickUser = (user_id) => {
        this.props.actions.kickUser(user_id);
    }

    handleInviteUsers = (payload) => {
        this.props.actions.inviteUsers(payload);
    }

    render() {
        return (
            <div className='app-container'>
                <CreateGroupChatModal
                    showModal={this.state.showCreateGroupChatModal}
                    onClose={this.handleCloseCreateGroupChatModal}
                    onCreate={this.handleCreateGroup}
                    users={this.props.users}
                />
                <LeaveGroupChatModal
                    showModal={this.state.showLeaveGroupChatModal}
                    onClose={this.handleCloseLeaveGroupChatModal}
                    onLeave={this.handleLeaveGroup}
                />
                <InfoGroupChatModal
                    showModal={this.state.showInfoGroupChatModal}
                    onClose={this.handleCloseInfoGroupChatModal}
                    onKick={this.handleKickUser}
                    onInvite={this.handleInviteUsers}
                    users={this.props.users}
                    chats={this.props.chats}
                />
                <div className ='chat-container'>
                    <UserList
                        createGroupModal={this.handleOpenCreateGroupChatModal}
                        setChatInitPendingState={this.setChatInitPendingState}
                        users={this.props.users}
                        chats={this.props.chats}
                        actions={this.props.actions}
                    />
                    <div className='app-inner-column'>
                        <ChatHeader
                            leaveGroupModal={this.handleOpenLeaveGroupChatModal}
                            infoGroupModal={this.handleOpenInfoGroupChatModal}
                            users={this.props.users}
                            chats={this.props.chats}
                            actions={this.props.actions}
                        />
                        <MessageList
                            setChatInitPendingState={this.setChatInitPendingState}
                            chatInitPending={this.state.chatInitPending}
                            users={this.props.users}
                            chats={this.props.chats}
                            actions={this.props.actions}
                            messages={this.props.messages}
                        />
                        <TypingList
                            typing={this.props.typing}
                            actions={this.props.actions}
                        />
                        <MessageForm
                            typing={this.props.typing}
                            actions={this.props.actions}
                        />
                    </div>
                </div>
                <div className='placeholder'>
                    <div className='header'></div>
                </div>
            </div>
        );
    }
}

function mapStateToProps (state) {
    return {
        users: state.get('users'),
        chats: state.get('chats'),
        messages: state.get('messages'),
        typing: state.get('typing'),
    };
}

function mapDispatchToProps (dispatch) {
    return {
        dispatch: dispatch,
        actions: bindActionCreators(actions, dispatch)
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(App);
