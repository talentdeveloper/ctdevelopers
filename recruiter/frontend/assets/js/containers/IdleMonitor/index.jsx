import React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import IdleTimer from 'react-idle-timer';

import * as actions from 'actions';

class IdleMonitor extends React.Component {
    constructor(props) {
        super(props);
        this.timeout = 60;
    }
    userIdle(isIdle){
        this.props.actions.userIdle(isIdle);
    }

    render() {
    return (<IdleTimer
      element={document}
      activeAction={this.userIdle.bind(this, false)}
      idleAction={this.userIdle.bind(this, true)}
      timeout={this.timeout * 1000} />);
    }
}

function mapStateToProps (state) {
    return {};
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
)(IdleMonitor);
