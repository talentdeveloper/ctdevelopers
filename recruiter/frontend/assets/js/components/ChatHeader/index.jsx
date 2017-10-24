import React from 'react';


const ChatHeader = (props) => {
    const { users, chats } = props
    const merged_users = users.merge(users.get('extra')).delete('extra').delete('self');
    let UI = <div />;
    if (chats.get('groups').get(chats.get('activeChat').toString())) {
        const participants = chats.get('groups').get(chats.get('activeChat').toString()).get('users');
        UI = (
            <div className='chat-header'>
                <div className='chat-header-pane-row'>
                    <span className='chat-header-names'>{chats.get('groups').get(chats.get('activeChat').toString()).get('name')}</span>
                    <div className='chat-header-actions'>
                        <span className='glyphicon glyphicon-user' onClick={props.infoGroupModal}></span>
                        <span className='glyphicon glyphicon-log-out' onClick={props.leaveGroupModal}></span>
                    </div>
                </div>
                <div className='chat-header-pane-row'>
                    <div className='chat-header-title group'>
                        {participants.mapEntries((entry, index) => {
                            return [index, <span key={entry[0]}>{merged_users.get(entry[0].toString()).get('name') + (index + 1 !== participants.size ? ', ' : '')}</span>]
                        }).toArray()}
                    </div>
                </div>
            </div>
        )
    } else if (chats.get('candidates').get(chats.get('activeChat').toString())) {
        UI = (
            <div className='chat-header'>
                <div className='chat-header-pane-row'>
                    <span className='chat-header-names'>{chats.get('candidates').get(chats.get('activeChat').toString()).get('name')}</span>
                </div>
                <div className='chat-header-pane-row'>
                    <span className='chat-header-title'>{chats.get('candidates').get(chats.get('activeChat').toString()).get('title')}</span>
                    {chats.get('candidates').get(chats.get('activeChat').toString()).get('location') ? <span className="chat-header-mark glyphicon glyphicon-map-marker"></span> : ''}
                    <span className='chat-header-location'>{chats.get('candidates').get(chats.get('activeChat').toString()).get('location')}</span>
                </div>
            </div>
        )
    }
    return UI;
}

export default ChatHeader
