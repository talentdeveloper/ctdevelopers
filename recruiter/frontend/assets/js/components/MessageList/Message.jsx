import React from 'react';
import moment from 'moment';
import urlRegex from 'url-regex';

class Message extends React.PureComponent {
    state = {
        loading: true,
        offlineMode: false
    }

    formatLinks = (message) => {
        const re = urlRegex({strict: false});
        if (message.search(re) !== -1) {
            const links = message.match(re);
            const splits = message.split(re);
            let result = [];
            for (let i = 0; i < splits.length; i++) {
                if (i === 0) {
                    result.push(splits[0]);
                } else {
                    let href = links[i-1];
                    if (!href.startsWith('http://') && !href.startsWith('https://')) {
                        href = `http://${href}`;
                    }
                    result.push(<a key={i} href={href} target='_blank'>{links[i-1]}</a>);
                    result.push(splits[i]);
                }
            }
            return result;
        } else return message;
    }

    humanizeSize = (bytes) => {
        const sufixes = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));

        return !bytes && '0 Bytes' || (bytes / Math.pow(1024, i)).toFixed(2) + " " + sufixes[i];
    }

    loadImage = (imagePath) => {
        let image = new Image(150, 150);
        image.onload = () => {
            this.setState({loading: false});
        }
        image.src = imagePath;
        return this.state.loading ? <div className="spinner-square">
            <div className="sk-fading-circle">
                {
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map(number => (
                        <div className={`sk-circle${number} sk-circle`} />))
                }
            </div></div> : <img src={imagePath} height="150" width="150"/>
    };
    render() {
        let userStatus = '';
        if(this.props.pendingId){
            setTimeout(function(){
                if(this.props.pendingId){
                    this.setState({offlineMode: true});
                }
            }.bind(this), 1500);
        }
        if(window.socket.websocket.readyState == 1){
            userStatus = this.props.user.get('online');
        }

        return (
            <div className={'message-list-item' + (this.props.pendingId ? ' pending': '')}>
                {}
                <div className={'user-avatar' + (userStatus === 2 ? ' user-online' : (userStatus === 1 ? ' user-away': ''))}>
                    <img src={this.props.user.get('photo')} />
                </div>
                <div className='message-list-item-body'>
                    <span className='message-list-item-name'>{this.props.user.get('name')}</span>
                    <div className='message-list-item-header'>
                        <div>
                            <p className='message-list-item-text'>{this.formatLinks(this.props.text)}</p>
                            <div className=''>{this.props.attachments.get('files').map((attachment, i) => {
                                if (/\.(jpe?g|png|gif)$/.test(attachment)){
                                    return <div key={i} >
                                            <a href={attachment} target="_blank" download={this.props.attachments.get('file_names').get(i)}>
                                                {this.loadImage(attachment)}
                                            </a>
                                            <div>
                                                <a href={attachment} target="_blank" download={this.props.attachments.get('file_names').get(i)}>{this.props.attachments.get('file_names').get(i)}</a>
                                                <span> {this.humanizeSize(this.props.attachments.get('file_sizes').get(i))}</span>
                                            </div>
                                        </div>
                                } else {
                                    return <div key={i}>
                                        <a href={attachment} target="_blank" download={this.props.attachments.get('file_names').get(i)}>{this.props.attachments.get('file_names').get(i)}</a>
                                        <span> {this.humanizeSize(this.props.attachments.get('file_sizes').get(i))}</span>
                                    </div>
                                }
                            })}</div>
                        </div>
                        <span className='message-list-item-time'>{moment(this.props.time, moment.ISO_8601).format('h:mm a')}</span>
                    </div>
                    {this.props.pendingId && this.state.offlineMode ? <div className='message-list-item-event offline-alert'><small>Currently offline - will be sent when online</small></div>: ''}
                    {this.props.group_invite && this.props.group_invite.get('status') === 1 ? <div className='message-list-item-event'><button onClick={() => props.onAccept(props.group_invite.get('conversation_id'), props.group_invite.get('invite_id'))} className='chat-button'>Accept</button><button onClick={() => props.onDecline(props.group_invite.get('conversation_id'), props.group_invite.get('invite_id'))} className='chat-button'>Decline</button></div> : ''}
                    {this.props.group_invite && this.props.group_invite.get('status') === 2 ? <div className='message-list-item-event'>Declined invitation</div> : ''}
                    {this.props.group_invite && this.props.group_invite.get('status') === 0 ? <div className='message-list-item-event'>Accepted invitation</div> : ''}
                </div>
            </div>
        );
    }
};

export default Message;
