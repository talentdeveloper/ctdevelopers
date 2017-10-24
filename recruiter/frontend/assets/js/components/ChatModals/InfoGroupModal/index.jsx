import React from 'react';
import ReactModal from 'react-modal';

import UserQueryForm from 'components/UserQueryForm';
import UserListItem from 'components/UserList/Item';


class InfoGroupChatModal extends React.PureComponent {
    state = {
        selectedUsers: [],
        groupMessage: '',
        valid: {
            users: true,
            message: true
        }
    }

    handleClose = () => {
        this.props.onClose();
        this.resetState();
    }

    handleKick = user_id => () => {
        this.props.onKick(parseInt(user_id));
    }

    handleInvite = (event) => {
        event.preventDefault();
        let valid = {...this.state.valid};
        if (this.state.groupMessage.length === 0) {
            valid.message = false;
        }
        if (this.state.selectedUsers.length === 0) {
            valid.users = false;
        }
        if (valid !== this.state.valid) {
            this.setState({valid});
        }
        setTimeout(() => {
            if (Object.values(this.state.valid).every(value => value)) {
                this.props.onInvite({
                    user_ids: this.state.selectedUsers.map(user => user.id),
                    message: this.state.groupMessage
                });
                this.resetState();
            }
        });
    }

    resetState() {
        this.setState({
            selectedUsers: [],
            groupMessage: '',
            valid: {
                users: true,
                message: true
            }
        });
        this.queryForm.resetState();
    }

    checkGroupMessage = () => {
        const groupMessage = this.groupMessageInput.value;
        this.setState({
            groupMessage
        });
        if (groupMessage.length > 0) {
            this.setState({
                valid: {...this.state.valid, message: true}
            });
        }
    }

    renderUsersGroup(users, header, owner) {
        if (users.size === 0) {
            return <div />;
        }
        const admin = this.props.users.get('self') === owner;
        users = users.sortBy((value, key) => key, (a, b) => {return parseInt(a) === owner ? -1 : (parseInt(b) === owner ? 1 : 0)});
        const merged_users = this.props.users.merge(this.props.users.get('extra')).delete('extra').delete('self');
        return (
            <div className='modal-control'>
                <label>{header}</label>
                {users.map((user, user_id) => {
                    let onAction = null;
                    if (admin && parseInt(user_id) !== owner) {
                        onAction = this.handleKick(user_id);
                    }
                    return <UserListItem key={user_id} user={merged_users.get(user_id.toString()).toJS()} onAction={onAction} />;
                }).toArray()}
            </div>
        );
    }

    renderInviteMoreUsersUI(users) {
        let activeUI = <div />;
        if (this.state.selectedUsers.length > 0) {
            activeUI = (
                <div>
                    <div id='group-message' className={'modal-control' + (this.state.valid.message ? '' : ' error')}>
                        <label>Message:</label>
                        <textarea
                            className='chat-input'
                            onKeyDown={this.checkGroupMessage}
                            onChange={this.checkGroupMessage}
                            ref={input => this.groupMessageInput = input}
                            value={this.state.groupMessage}
                        />
                    </div>
                    <button style={{marginTop: 20}} className='chat-button modal-button' type='submit' disabled={false}>
                        Invite
                    </button>
                </div>
            );
        }
        return (
            <form id='invite-more-form' onSubmit={this.handleInvite} autoComplete='off'>
                <UserQueryForm
                    id='user-invite'
                    label='Invite more people:'
                    users={users}
                    onChange={this.userQueryChange}
                    valid={true}
                    ref={queryForm => this.queryForm = queryForm}
                />
                {activeUI}
            </form>
        )
    }

    userQueryChange = (users) => {
        const selectedUsers = users;
        const valid = selectedUsers.length > 0;
        this.setState({
            selectedUsers,
            valid: {...this.state.valid, users: valid}
        });
    }

    render() {
        const {chats, users} = this.props;
        const chat = chats.get('groups').get(chats.get('activeChat').toString());
        if (!chat) {
            return <div />;
        }
        const active_users = chat.get('users').filter(user => user.get('status') === 0);
        const pending_users = chat.get('users').filter(user => user.get('status') === 1);
        const declined_users = chat.get('users').filter(user => user.get('status') === 2);
        const invitable_users = users.delete('self').delete('extra').delete(users.get('self').toString()).filter((user, id) => !active_users.has(id) && !pending_users.has(id));
        return (
            <ReactModal
                isOpen={this.props.showModal}
                contentLabel='Group chat info'
                onRequestClose={this.handleClose}
                style={{
                    overlay: {
                        top: '80px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }
                }}
                className='group-chat-modal'
            >
                <div className='group-chat-modal-header'>
                    <h3 style={{margin: 0}}>Chat group info</h3>
                    <span
                        className='glyphicon glyphicon-remove modal-close'
                        onClick={this.handleClose}
                    >
                    </span>
                </div>
                <div className='group-chat-modal-body'>
                    {this.renderUsersGroup(active_users, 'Joined users:', chat.get('owner'))}
                    {this.renderUsersGroup(pending_users, 'Pending invites:', chat.get('owner'))}
                    {this.renderUsersGroup(declined_users, 'Declined users:', chat.get('owner'))}
                </div>
                <div className='group-chat-modal-footer'>
                    {this.renderInviteMoreUsersUI(invitable_users)}
                </div>
            </ReactModal>
        );
    }
}

export default InfoGroupChatModal;
