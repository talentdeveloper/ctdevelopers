import React from 'react';
import ReactModal from 'react-modal';


const LeaveGroupChatModal = (props) => {
    const handleClose = () => {
        props.onClose();
    }

    const handleLeave = () => {
        props.onLeave();
    }
    return (
        <ReactModal
            isOpen={props.showModal}
            contentLabel='Leave group chat'
            onRequestClose={handleClose}
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
                <h3 style={{margin: 0}}>Leave chat group</h3>
                <span
                    className='glyphicon glyphicon-remove modal-close'
                    onClick={handleClose}
                >
                </span>
            </div>
            <div className='group-chat-modal-footer'>
                <button className='chat-button create-group-button' onClick={handleLeave}>
                    Yes
                </button>
                <button className='chat-button create-group-button' onClick={handleClose}>
                    No
                </button>
            </div>
        </ReactModal>
    );
}

export default LeaveGroupChatModal;
