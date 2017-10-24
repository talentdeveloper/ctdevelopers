import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import moment from 'moment';
import IdleTimer from 'react-idle-timer';

var axios = require('axios');

var STATUS_OPEN = 0;
var STATUS_WAIT_CLIENT = 1;
var STATUS_WAIT_PROVIDER = 2;
var STATUS_CLOSE = 3;

var status_to_css_class = {}
status_to_css_class[STATUS_OPEN] = 'badge progress-bar-danger';
status_to_css_class[STATUS_WAIT_CLIENT] = 'badge progress-bar-warning';
status_to_css_class[STATUS_WAIT_PROVIDER] = 'badge progress-bar-danger';
status_to_css_class[STATUS_CLOSE] = 'badge progress-bar-success';

class IssueMonitor extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            issue: {seconds_left: 1800},
            should_bother: false
        }
        this.displayState = this.displayState.bind(this);
        this.handleCloseIssueClick = this.handleCloseIssueClick.bind(this);
    }

    displayState() {
        var uuid = this.state.issue_uuid;
        axios.get(`/support/issue/${uuid}/api/`)
            .then(res => {
                const issue = res.data;
                this.setState({issue})
            });
    }

    handleCloseIssueClick() {
        var uuid = this.state.issue.uuid;
        axios.get(`/support/issue/${uuid}/close/api/`)
            .then(res => {
                console.log("Issue was closed")
            });
    }

    fetchIssueForChat(conversation) {
        axios.get(`/support/issue/conversation/${conversation}/api/`)
            .then(res => {
                const issue_uuid = res.data.issue.uuid;
                this.setState({issue_uuid})
                this.should_bother = true;
                this.timerID = setInterval(
                    () => this.displayState(),
                    1000
                );
            })
            .catch(err => {
                // TODO: handle error properly
                this.should_bother = false;
            })
    }

    componentWillReceiveProps(nextProps) {
        this.fetchIssueForChat(nextProps.conversation);
    }

    componentDidMount() {
        this.fetchIssueForChat(this.props.conversation);
    }

    componentWillUnmount() {
        clearInterval(this.timerID);
    }

    formatDate(date) {
        const now = moment();
        const then = moment(date);
        return then.format('HH:mm dddd, MMM Do, YYYY');
    }

    issueInfo(issue) {
        return (
            <div>
                <p className="small">
                    Issue opened on<br/>
                    {this.formatDate(issue.created_at)}
                </p>
                <p className="small">
                    Last updated at<br/>
                    {this.formatDate(issue.updated_at)}
                </p>
            </div>
        );
    }

    maybeRenderSLA(issue) {
        var seconds_left = issue.seconds_left;
        var minutes = parseInt(seconds_left / 60, 10);
        var seconds = parseInt(seconds_left % 60, 10);
        if (issue.status != STATUS_CLOSE) {
            return (<p>
                SLA ends in&nbsp;
                <span className="badge progress-bar-danger">{minutes}</span>
                &nbsp;<b>:</b>&nbsp;
                <span className="badge progress-bar-danger">{seconds}</span>
            </p>);
        } else {
            return <hr/>;
        }
    }

    render() {
        if (this.should_bother) {
            var issue = this.state.issue;

            let button = null;
            if (issue.status != STATUS_CLOSE) {
               button = <button
                className='chat-button send-button'
                onClick={this.handleCloseIssueClick}
                >
                    Close Issue
                </button>;
            }

            return (
            <div className="row text-center">
                {issue.status != STATUS_CLOSE ?
                    <h3>Ongoing Issue</h3> :
                    <h3>Recent Issue</h3>
                }
                <p>Subject: {issue.subject}</p>
                <p>
                    Current status:
                    <span className={status_to_css_class[issue.status]}>
                      {issue.status_humanreadable}
                    </span>
                </p>
                {this.issueInfo(issue)}
                {this.maybeRenderSLA(issue)}
                {button}
            </div>
            );
        } else {
            return null;
        }
    }
}

export default IssueMonitor;
