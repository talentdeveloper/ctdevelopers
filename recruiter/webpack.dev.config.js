const webpack = require('webpack');
//const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;


let config = require('./webpack.base.config.js');

config.devtool = 'inline-source-map';

config.entry = [
    'react-hot-loader/patch',
    'webpack-dev-server/client?http://localhost:3000',
    'webpack/hot/only-dev-server',
    './frontend/assets/js/index.jsx'
];

config.output.publicPath = 'http://localhost:3000/static/';

config.plugins = config.plugins.concat([
    /*new BundleAnalyzerPlugin({
        analyzerMode: 'static'
    }),*/
    new webpack.HotModuleReplacementPlugin(),
    new webpack.NamedModulesPlugin(),
    new webpack.NoEmitOnErrorsPlugin()
]);

config.module.rules[0].use.options.plugins = ['transform-object-rest-spread', 'babel-plugin-syntax-dynamic-import', 'react-hot-loader/babel'];

module.exports = config;
