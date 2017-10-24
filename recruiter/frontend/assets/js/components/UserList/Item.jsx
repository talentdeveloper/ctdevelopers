import React from 'react';

const UserListItem = (props) => {
    const {user, onAction} = props;
    return (
        <div className='users-query-list-item'>
            <div className={'user-avatar small' + (user.online === 2 ? ' user-online' : ((user.online) === 1 ? ' user-away': ''))}>
                <img src={user.photo} />
            </div>
            <span className='users-query-list-item-name'>
                {`${user.name} <${user.email}>`}
            </span>
            {onAction ? <span style={{fontSize: '20px', marginLeft: '5px', cursor: 'pointer'}} className='glyphicon glyphicon-minus-sign' onClick={onAction} /> : '' }
        </div>
    );
};

export default UserListItem;
