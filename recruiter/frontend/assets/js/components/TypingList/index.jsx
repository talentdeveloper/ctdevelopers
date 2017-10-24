import React from 'react';


class TypingList extends React.Component {
    userTypingExpireTime = 3

    componentWillReceiveProps(nextProps) {
        const { typing } = nextProps;
        typing.get('typingMap').entrySeq().forEach(entry => {
            if (entry[1].get('timer_id') === 0) {
                const timer_id = setTimeout(() => {
                    this.props.actions.typeTimerExpire({
                        user_id: entry[0],
                        user_name: entry[1].get('user_name'),
                        timer_id
                    });
                }, this.userTypingExpireTime * 1000);
                this.props.actions.typeTimerStart({
                    user_id: entry[0],
                    user_name: entry[1].get('user_name'),
                    timer_id
                });
            }
        });
    }

    render() {
        const { typing } = this.props;
        let typingUI = <div />;
        if (typing.get('typingMap').size > 1) {
            let typingString = '';
            typing.get('typingMap').reduce(
                (result, user) => {
                    if (typingString.length !== 0) {
                        typingString += ', '
                    }
                    typingString += user.get('user_name');
                },
                typingString
            );
            typingUI = <div className='user-type-list-item'>{`${typingString} are typing...`}</div>;
        } else if (typing.get('typingMap').size === 1) {
            typingUI = <div className='user-type-list-item'>{typing.get('typingMap').first().get('user_name') + ' is typing...'}</div>;
        }
        return (
            <div className='user-type-list'>
                {typingUI}
            </div>
        );
    }
}

export default TypingList
