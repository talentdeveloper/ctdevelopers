import { connect } from 'react-redux';
import { bindActionCreators } from 'redux';
import React from 'react';
import moment from 'moment';
import shallowEqual from 'shallowequal';

import * as actions from 'actions';


class MessageForm extends React.Component {
    constructor(props){
        super(props);

        this.state = {
            valid: false,
            message: '',
            files: {
                name: [],
                file: [],
                size: [],
            },
            file_names: [],
            file_sizes: [],
        };
        this.lastInput = null;
        this.typingThrottleTime = 3;
    }

    onSend = (event) => {
        event.preventDefault();
        if (!this.state.valid) {
            return;
        }

        this.props.actions.sendMessage({
            conversation_id: this.props.typing.get('activeChat'),
            message: this.state.message,
            attachment: this.state.files
        });

        this.textInput.focus();
        this.setState({
            valid: false,
            message: '',
            files: {
                name: [],
                file: [],
                size: [],
            },
            file_names: [],
            file_sizes: [],
        });
    }

    resetForm() {
        document.getElementById('message-form').reset();
    }

    shouldComponentUpdate(nextProps, nextState) {
        return (
            !shallowEqual(this.state, nextState)
            || this.props.typing.get('activeChat') != nextProps.typing.get('activeChat')
            || this.props.socketIsConnected != nextProps.socketIsConnected
        );
    };

    humanizeSize = (bytes) => {
        const sufixes = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));

        return !bytes && '0 Bytes' || (bytes / Math.pow(1024, i)).toFixed(2) + " " + sufixes[i];
    }

    _handleImageChange(event, flag) {
        event.preventDefault();

        let reader = new FileReader();
        let progressBar = document.querySelector('#upload-progress');
        let submitButton = document.querySelector('#submit-button');
        if (flag) {
            let file = event.target.files[0];
            if (file.size < 5242880) {
                this.setState({
                    file_names: this.state.file_names.concat(event.target.files[0].name),
                    file_sizes: this.state.file_sizes.concat(event.target.files[0].size)
                })

                reader.onprogress = (response) => {
                    const progress = parseInt( ((response.loaded / response.total) * 100), 10 );
                    progressBar.style.display = 'block';

                    if (progress >= 100) {
                        progressBar.style.display = 'none';
                        submitButton.removeAttribute('disabled');
                    } else {
                        progressBar.style.width = progress + '%';
                        submitButton.setAttribute('disabled', true);
                    }
                }

                reader.onloadend = (response) => {
                    this.setState({
                        files: {
                            name: this.state.files.name.concat(file.name),
                            file: this.state.files.file.concat(response.target.result),
                            size: this.state.files.size.concat(file.size),
                        },
                        valid: true
                    });
                }
                this.resetForm()
                reader.readAsDataURL(file)
            } else {
                alert('File size too big. Maximum file size is 5 MB');
            }
        } else {
            this.setState({
                file_names: [],
                file_sizes: [],
                files: {
                    name: [],
                    file: [],
                    size: [],
                },
            })
            if (!this.state.message) {
                this.setState({
                    valid: false
                })
            }
            progressBar.style.display = 'none';
            this.resetForm();
        }
    }

    checkInput = (event) => {
        if ((this.lastInput === null || (moment().unix() - this.lastInput >= this.typingThrottleTime))
            && this.props.typing.get('activeChat') !== 0){

            this.lastInput = moment().unix();
            this.props.actions.userTyping();
        }

        const message = event.target.value;
        const valid = message && message.length > 0;
        this.setState({ valid, message });
    }

    render() {
        const submitDisabled = !this.state.valid;
        let inputStyle = {};
        if(this.props.socketIsConnected == false){
            inputStyle['backgroundColor'] = 'rgba(249, 249, 121, 0.61)';
        }
        return (
            <div>
                <form id='message-form' onSubmit={this.onSend} encType="multipart/form-data">
                    <input className='chat-input message-input'
                        ref={input => this.textInput = input}
                        type='text'
                        placeholder='Say something nice'
                        maxLength='1024'
                        style={inputStyle}
                        onChange={this.checkInput}
                        onKeyDown={this.checkInput}
                        value={this.state.message}
                    />
                    <div>
                        <label htmlFor="file-attachment" className="glyphicon glyphicon-pushpin attachment-pushpin attachment-remove"/>
                        <input className="hidden"
                            id="file-attachment"
                            type="file"
                            onChange={(event)=>this._handleImageChange(event, true)} />
                        <i id='remove-files' className="glyphicon glyphicon-remove attachment-pushpin" onClick={(event) => this._handleImageChange(event, false)}></i>
                    </div>
                    <button id='submit-button' className='chat-button send-button' type='submit' disabled={submitDisabled}>
                        Send
                    </button>
                </form>
                <div id="upload-progress-bar">
                    <div id="upload-progress"></div>
                </div>

                <div className="chat-file-names">
                    {this.state.file_names.length && this.state.files.file.length ?
                        this.state.file_names.map((file_name, i) => {
                            if (!(/^data:image\/(jpe?g|png|gif);/.test(this.state.files.file[i]))) {
                                return <div key={i}>
                                    <span>{file_name}</span>
                                    <span> {this.humanizeSize(this.state.file_sizes[i])}</span>
                                </div>
                            } else {
                                return <div key={i}>
                                    <span>{file_name}</span>
                                    <span> {this.humanizeSize(this.state.file_sizes[i])}</span>
                                    <div>
                                        <img id="image-preview" src={this.state.files.file[i]} width="150" height="150"/>
                                    </div>
                                </div>
                            }
                        })
                        :
                        ''
                    }
                </div>
            </div>
        );
    }
}


function mapStateToProps (state) {
    return {
        socketIsConnected: state.get('chats').get('socketIsConnected')
    };
}

function mapDispatchToProps (dispatch) {
    return {
        dispatch: dispatch,
        actions: bindActionCreators(actions, dispatch)
    };
}

export default connect(
    mapStateToProps,
    mapDispatchToProps
)(MessageForm);
