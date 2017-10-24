import React from 'react';
import ReactModal from 'react-modal';

import UserQueryForm from 'components/UserQueryForm';


class CreateGroupChatModal extends React.PureComponent {
    state = {
        groupName: '',
        groupMessage: '',
        valid: {
            users: true,
            name: true,
            message: true
        },
        selectedUsers: []
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

    checkGroupName = () => {
        const groupName = this.groupNameInput.value;
        this.setState({
            groupName
        });
        if (groupName.length > 0) {
            this.setState({
                valid: {...this.state.valid, name: true}
            });
        }
    }

    resetState() {
        this.setState({
            groupName: '',
            groupMessage: '',
            selectedUsers: [],
            valid: {
                users: true,
                name: true,
                message: true
            }
        });
    }

    handleClose = () => {
        this.props.onClose();
        this.resetState();
    }

    handleCreate = (event) => {
        event.preventDefault();
        let valid = {...this.state.valid};
        if (this.state.groupName.length === 0) {
            valid.name = false;
        }
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
                this.props.onCreate(this.state.selectedUsers.map(user => user.id), this.state.groupName, this.state.groupMessage);
                this.resetState();
            }
        });
    }

    userQueryChange = (users) => {
        const valid = users.length > 0;
        this.setState({
            selectedUsers: users,
            valid: {...this.state.valid, users: valid}
        });
    }

    render() {
        return (
            <ReactModal
                isOpen={this.props.showModal}
                contentLabel='Create group chat'
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
                    <h3 style={{margin: 0}}>Create Chat Group</h3>
                    <span
                        className='glyphicon glyphicon-remove modal-close'
                        onClick={this.handleClose}
                    >
                    </span>
                </div>
                <form id='create-group-form' onSubmit={this.handleCreate} autoComplete='off'>
                    <div className='group-chat-modal-body'>
                        <UserQueryForm
                            id='user-search'
                            label='Add person:'
                            users={this.props.users.delete('self').delete('extra').delete(this.props.users.get('self').toString())}
                            onChange={this.userQueryChange}
                            valid={this.state.valid.users}
                        />
                        <div id='group-name' className={'modal-control' + (this.state.valid.name ? '' : ' error')}>
                            <label>Group name:</label>
                            <input
                                className='chat-input'
                                type='text'
                                onKeyDown={this.checkGroupName}
                                onChange={this.checkGroupName}
                                ref={input => this.groupNameInput = input}
                                value={this.state.groupName}
                            />
                        </div>
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
                    </div>
                    <div className='group-chat-modal-footer'>
                        <button className='chat-button modal-button' type='submit' disabled={false}>
                            Create Group
                        </button>
                    </div>
                </form>
            </ReactModal>
        );
    }
}

export default CreateGroupChatModal;
