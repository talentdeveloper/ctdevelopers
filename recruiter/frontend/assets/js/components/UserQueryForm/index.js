import React from 'react';
import { Scrollbars } from 'react-custom-scrollbars';

import UserListItem from 'components/UserList/Item';


class UserQueryForm extends React.PureComponent {
    state = {
        userSearchQuery: '',
        selectedUsers: [],
        queryUsers: [],
        activeQueryIndex: 0,
        queryUserDOMHeight: 30
    }

    selectUser = index => () => {
        const selectedUsers = [...this.state.selectedUsers, this.state.queryUsers[index]];
        this.setState({
            selectedUsers,
            activeQueryIndex: 0,
            userSearchQuery: '',
            queryUsers: []
        });
        this.props.onChange(selectedUsers);
    }

    handleKeyPress = (event) => {
        if (event.key === 'ArrowDown') {
            if (this.state.queryUsers.length > 1) {
                if (this.state.activeQueryIndex < this.state.queryUsers.length - 1) {
                    const scrollValues = this.scroll.getValues();
                    const activeQueryIndex = this.state.activeQueryIndex + 1;
                    const activeElementScroll = this.state.queryUserDOMHeight*(activeQueryIndex + 1);
                    if (activeElementScroll > scrollValues.scrollTop + scrollValues.clientHeight) {
                        this.scroll.scrollTop(scrollValues.scrollTop + this.state.queryUserDOMHeight);
                    }
                    this.setState({activeQueryIndex});
                } else {
                    this.setState({activeQueryIndex: 0});
                    this.scroll.scrollToTop();
                }
            }
            event.preventDefault();
            return;
        }
        if (event.key === 'ArrowUp') {
            if (this.state.queryUsers.length > 1) {
                if (this.state.activeQueryIndex > 0) {
                    const scrollValues = this.scroll.getValues();
                    const activeQueryIndex = this.state.activeQueryIndex - 1;
                    const activeElementScroll = this.state.queryUserDOMHeight*(activeQueryIndex);
                    if (activeElementScroll < scrollValues.scrollTop) {
                        this.scroll.scrollTop(scrollValues.scrollTop - this.state.queryUserDOMHeight);
                    }
                    this.setState({activeQueryIndex});
                } else {
                    this.setState({activeQueryIndex: this.state.queryUsers.length - 1});
                    this.scroll.scrollToBottom();
                }
            }
            event.preventDefault();
            return;
        }
        if (event.key === 'Enter' || event.key === 'Tab') {
            event.preventDefault();
            if (this.state.queryUsers.length > 0) {
                return this.selectUser(this.state.activeQueryIndex)();
            }
        }
        this.searchUsers();
    }

    searchUsers = () => {
        const {users} = this.props;
        const userSearchQuery = this.userSearchInput.value;
        if (userSearchQuery !== this.state.userSearchQuery) {
            this.setState({userSearchQuery});
            this.setState({activeQueryIndex: 0});
            if (userSearchQuery.length > 0) {
                let queryUsers = users.filter(user => {
                    const has_name = user.get('name').toLowerCase().includes(userSearchQuery.toLowerCase());
                    const has_email = user.get('email').toLowerCase().includes(userSearchQuery.toLowerCase());
                    return has_email || has_name;
                });
                queryUsers = queryUsers.map((user, id) => {
                    return user.set('id', parseInt(id)).toObject();
                }).toArray();
                const selected_ids = this.state.selectedUsers.map(user => user.id);
                queryUsers = queryUsers.filter(user => !selected_ids.some(id => id === user.id));
                this.setState({queryUsers});
            } else {
                this.setState({queryUsers: []});
            }
        }
    }

    removeSelectedUser = index => () => {
        const {selectedUsers} = this.state;
        selectedUsers.splice(index, 1);
        this.setState(selectedUsers);
        this.props.onChange(selectedUsers);
    }

    resetState() {
        this.setState({
            userSearchQuery: '',
            selectedUsers: [],
            queryUsers: [],
            activeQueryIndex: 0
        });
    }

    render() {
        let usersQueryUI = '';
        if (this.state.queryUsers.length > 0) {
            const height_max = this.state.queryUserDOMHeight*5;
            const height = Math.min(this.state.queryUsers.length * this.state.queryUserDOMHeight, height_max);
            usersQueryUI = (
                <div className='users-query-list' style={{height}}>
                    <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                                style={{height: '100%'}}
                                autoHide autoHideTimeout={1000}
                                autoHideDuration={200}
                    >
                        {this.state.queryUsers.map((user, index) => {
                            return (
                                <div
                                    key={index}
                                    className={'users-query-list-item' + (index === this.state.activeQueryIndex ? ' active' : '')}
                                    onClick={this.selectUser(index)}
                                >
                                    {`${user.name} <${user.email}>`}
                                </div>
                            );
                        })}
                    </Scrollbars>
                </div>
            );
        }
        let selectedUsersUI = '';
        if (this.state.selectedUsers.length > 0) {
            selectedUsersUI = (
                <div>
                    <div className={'well' + (this.state.selectedUsers.length > 0 ? '' : ' hidden')}>
                        {this.state.selectedUsers.map((user, index) => {
                            return <UserListItem key={index} user={user} onAction={this.removeSelectedUser(index)} />;
                        })}
                    </div>
                </div>
            );
        }
        return (
            <div id={this.props.id} className={'user-query-container modal-control' + (this.props.valid ? '' : ' error')}>
                <label>{this.props.label}</label>
                <input
                    type='text'
                    className='chat-input'
                    onKeyDown={this.handleKeyPress}
                    onChange={this.searchUsers}
                    ref={input => this.userSearchInput = input}
                    value={this.state.userSearchQuery}
                    placeholder='Search person by name or email'
                />
                {usersQueryUI}
                {selectedUsersUI}
            </div>
        );
    }
}

export default UserQueryForm;
