import 'babel-polyfill';

import React from 'react';
import ReactDOM from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware, compose } from 'redux';
import thunkMiddleware from 'redux-thunk';
import { AppContainer } from 'react-hot-loader';

import App from 'containers/Chat';
import IdleMonitor from 'containers/IdleMonitor';
import GlobalMessagesNotification from 'containers/GlobalMessagesNotification';
import rootReducer from 'reducers';
import { init as websocketInit, emit } from 'actions/websocket';


(function startUp() {
    const thunk = thunkMiddleware.default ? thunkMiddleware.default : thunkMiddleware;
    const middleware = [thunk.withExtraArgument({emit})];

    const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
    const store = createStore(rootReducer, /* preloadedState, */ composeEnhancers(
        applyMiddleware(...middleware)
    ));
    websocketInit(store); // setup websocket listeners etc

    if (module.hot) {
        // Enable Webpack hot module replacement for reducers
        module.hot.accept('./reducers', () => {
            const nextRootReducer = import('./reducers/index.js');
            store.replaceReducer(nextRootReducer);
        });
    }

    window.storeRoot = store;
}());

const render = (Component, container) => {
    ReactDOM.render(
        <AppContainer>
            <Provider store={window.storeRoot}>
                <Component />
            </Provider>
        </AppContainer>,
        container
    );
};

if (window.location.pathname.startsWith('/chat/')) {
    render(App, document.getElementById('app'));
}

const divIdle = document.createElement('div');
divIdle.id = 'idle-monitor';
document.getElementsByTagName('body')[0].appendChild(divIdle);
render(IdleMonitor, divIdle);

render(GlobalMessagesNotification, document.getElementById('global-messages-notification'));

if (module.hot) {
    if (window.location.pathname.startsWith('/chat/')) {
        module.hot.accept('containers/Chat', () => {
            ReactDOM.unmountComponentAtNode(document.getElementById('app'));
            render(App, document.getElementById('app'));
        });
    }
    module.hot.accept('containers/IdleMonitor', () => {
        ReactDOM.unmountComponentAtNode(divIdle);
        render(IdleMonitor, divIdle);
    });
    module.hot.accept('containers/GlobalMessagesNotification', () => {
        ReactDOM.unmountComponentAtNode(document.getElementById('global-messages-notification'));
        render(GlobalMessagesNotification, document.getElementById('global-messages-notification'));
    });
}
