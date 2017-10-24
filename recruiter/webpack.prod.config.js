const path = require('path');
const glob = require('glob-all');
const webpack = require('webpack');

let config = require('./webpack.base.config.js');


config.output.filename = '[name].[chunkhash].js';

config.devtool = 'source-map';

config.plugins = config.plugins.concat([
    new webpack.optimize.CommonsChunkPlugin({
        name: 'chat-vendor',
        minChunks: function (module) {
            return module.context && module.context.indexOf('node_modules') >= 0;
        }
    }),
    new webpack.optimize.CommonsChunkPlugin({
        name: 'manifest'
    }),
    new webpack.LoaderOptionsPlugin({
        minimize: true,
        debug: false
    }),
    new webpack.optimize.UglifyJsPlugin({
        sourceMap: config.devtool && (config.devtool.indexOf("sourcemap") >= 0 || config.devtool.indexOf("source-map") >= 0),
        beautify: false,
        mangle: {
            screw_ie8: true,
            keep_fnames: true
        },
        compress: {
            screw_ie8: true
        },
        comments: false
    }),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify('production')
    })
]);

module.exports = config;
