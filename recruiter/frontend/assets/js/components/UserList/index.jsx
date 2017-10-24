import React from 'react';
import { Scrollbars } from 'react-custom-scrollbars';
import shallowEqual from 'shallowequal';
import moment from 'moment';
import { Loader } from 'react-loaders';


class UserList extends React.Component {
    state = {
        selectedUsersGroup: 0
    }

    userPresencePollingInterval = 10

    componentDidMount() {
        this.initializeChat();  // open last chat
        setInterval(() => this.props.actions.userPresence(), this.userPresencePollingInterval * 1000);
        setInterval(() => this.props.actions.resendAllPendingMessages(), 1000);
    }

    shouldComponentUpdate = function (nextProps, nextState) {
        return !shallowEqual(this.state, nextState) || !shallowEqual(this.props, nextProps);
    };

    initializeChat(seconds=100, attempts=0) {
        if (attempts > 20) return;

        if (window.socket.websocket.readyState === 1) {
            const { chats } = this.props;
            ['candidates', 'agents', 'groups',].some((group, index) => {
                if (chats.get(group).size > 0) {
                    // open group where last chat is
                    this.handleUserGroupSelect(index)
                    // open last chat
                    this.chatInit(chats.get(group).keys().next().value)
                    return true
                } else return false;
            })
        } else {
            // if socket is not ready yet then wait `seconds` and try again
            setTimeout(() => this.initializeChat(seconds + 100, attempts + 1), seconds)
        }
    }

    componentWillReceiveProps(nextProps) {
        // send initChat again after reconnect
        if(
            nextProps.chats.get('chatInitialized') == false
            && nextProps.chats.get('activeChat') == 0
            && this.props.chats.get('activeChat') != 0
        ){
            this.props.actions.initChat(this.props.chats.get('activeChat'), true);
            return;
        }

        const activeChat = nextProps.chats.get('activeChat');
        if (this.props.chats.get('activeChat') !== activeChat) {
            ['candidates', 'agents', 'groups'].some((group, index) => {
                const value = nextProps.chats.get(group).find((chat, conversation_id) => parseInt(conversation_id) === activeChat);
                if (value) {
                    this.setState({selectedUsersGroup: index});
                    return true;
                } else return false;
            });
        }
    }

    chatInit(id) {
        if (parseInt(id) === this.props.chats.get('activeChat')) {
            return;
        }
        this.props.setChatInitPendingState(true);
        this.props.actions.initChat(id);
    }

    formatDate(date) {
        const now = moment();
        const then = moment(date);
        if (then.isSame(now, 'day')) {
            return then.format('h:mm a');
        } else {
            return then.format('DD/MM/YYYY');
        }
    }

    renderUsersGroup(chats, group_name) {
        if (this.props.users.get('self') === 0) {
            return <Loader className='empty-user-group' type='ball-pulse' active />;
        }
        if (chats.size === 0) {
            return <div className='empty-user-group'>You have no {group_name}</div>
        }
        const {users} = this.props;
        return chats.map((chat, conversation_id) => {
            const show_last_message = chat.get('last_message_text') !== '';
            // TODO: Figure out something for group avatar.
            return (
                <div
                    onClick={() => {this.chatInit(conversation_id)}}
                    key={conversation_id}
                    className={'user-list-item' + (parseInt(conversation_id) === this.props.chats.get('activeChat') ? ' active' : '') + (chat.get('unread') > 0 ? ' unread' : '')}
                >
                    <div className='user-list-item-div'>
                        {chat.get('user') ?
                            <div className={'user-avatar' + (users.get(chat.get('user').toString()).get('online') === 2 ? ' user-online' : (users.get(chat.get('user').toString()).get('online') === 1 ? ' user-away': ''))}>
                                <img src={users.get(chat.get('user').toString()).get('photo')} />
                            </div> :
                            <div className='group-avatar'>
                                <img src={users.get(users.get('self').toString()).get('photo')} />
                            </div>
                        }
                        <div className='user-list-item-pane'>
                            <div className='user-list-item-pane-row'>
                                <span className='user-list-item-name'>{chat.get('name')}</span>
                                {chat.get('unread') > 0 ? <div className='user-list-item-unread'><span>New Message</span></div> :
                                show_last_message ? <span className='user-list-item-timestamp'>{this.formatDate(chat.get('last_message_time'))}</span> : ''}
                            </div>
                            {chat.get('user') ?
                                <div className='user-list-item-pane-row'>
                                    {users.get(chat.get('user').toString()).get('location') ? <span className="user-list-item-mark glyphicon glyphicon-map-marker"></span> :
                                    ''}
                                    <span className='user-list-item-location'>{users.get(chat.get('user').toString()).get('location')}</span>
                                </div> : ''
                            }
                            {chat.get('user') ?
                                <div className='user-list-item-pane-row'>
                                    <span className='user-list-item-title'>{users.get(chat.get('user').toString()).get('title')}</span>
                                </div> : ''
                            }
                            <div className='user-list-item-pane-row'>
                                {show_last_message ? <span className='user-list-item-message'>{chat.get('last_message_text')}</span> : ''}
                            </div>
                        </div>
                    </div>
                </div>
            );
        }).toArray();
    }

    handleUserGroupSelect = group => () => {
        this.setState({selectedUsersGroup: group});
    }

    render() {

        const {chats} = this.props;
        const {users} = this.props;
        const unreadCandidates = chats.get('candidates').reduce((result, user) => result + user.get('unread'), 0);
        const unreadAgents = chats.get('agents').reduce((result, user) => result + user.get('unread'), 0);
        const unreadGroups = chats.get('groups').reduce((result, user) => result + user.get('unread'), 0);

        let userListUI = '';
        if (this.state.selectedUsersGroup === 0) {
            userListUI = this.renderUsersGroup(chats.get('candidates'), 'team network connections');
        } else if (this.state.selectedUsersGroup === 1) {
            userListUI = this.renderUsersGroup(chats.get('agents'), 'agents connections');
        } else if (this.state.selectedUsersGroup === 2) {
            userListUI = this.renderUsersGroup(chats.get('groups'), 'group conversations');
        }


        let account_type = 0;
        if (users.get('self') !== 0) {
            account_type = users.get(users.get('self').toString()).get('account_type');
        }

        return (
            <div className='user-list-container'>
                <Scrollbars ref={(scroll) => {this.scroll = scroll;}}
                                style={{height: '100%'}}
                                autoHide autoHideTimeout={1000}
                                autoHideDuration={200}>
                    <div className='user-list'>
                        <div className='user-list-header'>
                            <div className='user-list-header-div'>
                                <button className={'chat-button user-list-button button-candidates' + (this.state.selectedUsersGroup === 0 ? ' active' : '')} onClick={this.handleUserGroupSelect(0)}>
                                    {
                                        account_type == 1 ?
                                        'My Team':
                                        'Candidates'
                                    }
                                    {
                                        this.state.selectedUsersGroup !== 0 && unreadCandidates !== 0 ?
                                        <span>{unreadCandidates}</span> :
                                        ''
                                    }
                                </button>
                                <button className={'chat-button user-list-button button-agents' + (this.state.selectedUsersGroup === 1 ? ' active' : '')} onClick={this.handleUserGroupSelect(1)}>
                                    Agents
                                    {
                                        this.state.selectedUsersGroup !== 1 && unreadAgents !== 0 ?
                                        <span>{unreadAgents}</span> :
                                        ''
                                    }
                                </button>
                                <button className={'chat-button user-list-button button-groups' + (this.state.selectedUsersGroup === 2 ? ' active' : '')} onClick={this.handleUserGroupSelect(2)}>
                                    Groups
                                    {
                                        this.state.selectedUsersGroup !== 2 && unreadGroups !== 0 ?
                                        <span>{unreadGroups}</span> :
                                        ''
                                    }
                                </button>
                                <a className='chat-button user-list-button button-mail' href={Urls['mail:alert_list']()}><i className='glyphicon glyphicon-envelope'></i></a>
                            </div>
                        </div>
                        <div className='user-list-group'>
                            <div className='user-list-search'>
                                <input type='text' className='form-control' placeholder='Search' />
                            </div>
                            {this.state.selectedUsersGroup === 2 ? <div onClick={this.props.createGroupModal} id='create-conversation'><span className='glyphicon glyphicon-plus'></span> Create New Group</div> : ''}
                            {userListUI}
                        </div>
                    </div>
                </Scrollbars>
            </div>
        );
    }
}

export default UserList
