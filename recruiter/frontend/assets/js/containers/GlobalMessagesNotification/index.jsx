import React from 'react';
import { connect } from 'react-redux';


const GlobalMessagesNotification = (props) => {
    const originalTitle = document.title
    const unread_candidates = props.chats.get('candidates').reduce((result, chat) => result + chat.get('unread'), 0);
    const unread_agents = props.chats.get('agents').reduce((result, chat) => result + chat.get('unread'), 0);
    const unread_groups = props.chats.get('groups').reduce((result, chat) => result + chat.get('unread'), 0);
    const unread_sum = unread_candidates + unread_agents + unread_groups
    if (unread_sum > 0) {
        if (/^\[\d+\]/.test(originalTitle)) {
            document.title = document.title.replace(/^\[\d+\]/, `[${unread_sum}]`)
        } else {
            document.title = `[${unread_sum}] ${originalTitle}`;
        }
        return (
            <span style={{
                borderRadius: 3,
                width: 20,
                height: 20,
                backgroundColor: '#37a000',
                color: 'white',
                fontWeight: 700,
                textAlign: 'center'}}
            >
                {unread_sum}
            </span>
        );
    } else {
        document.title = originalTitle.replace(/^\[\d+\]/, '');
        return <div />;
    }
}

function mapStateToProps (state) {
    return {
        chats: state.get('chats')
    };
}

export default connect(
    mapStateToProps
)(GlobalMessagesNotification);
