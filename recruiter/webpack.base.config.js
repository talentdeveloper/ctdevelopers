 const path = require('path');
const BundleTracker = require('webpack-bundle-tracker');
const ExtractTextPlugin = require('extract-text-webpack-plugin');
const CopyWebpackPlugin = require('copy-webpack-plugin');


const extractSass = new ExtractTextPlugin({filename: '[name].[contenthash].css', allChunks: true, disable: process.env.NODE_ENV !== "production"});

module.exports = {
    context: __dirname,
    entry: {
        chat: './frontend/assets/js/index.jsx'
    },
    output: {
        path: path.resolve('./dist/'),
        filename: '[name].js',
        sourceMapFilename: '[name].js.map',
        publicPath: '/static/',
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        extractSass,
        new CopyWebpackPlugin([{
            context: './frontend/static.prod',
            from: '**/*',
            to: './'
        }])
    ],
    resolve: {
        extensions: ['.webpack-loader.js', '.web-loader.js', '.loader.js', '.js', '.jsx'],
        modules: [
            path.resolve(__dirname, 'node_modules'),
            path.resolve(__dirname, 'frontend', 'assets', 'js'),
        ],
      },
    module: {
        rules: [
        {
            test: /\.jsx?$/,
            use: {
                loader: 'babel-loader',
                options: {
                    presets: [['env', {modules: false}], 'react', 'es2015', 'stage-0'],
                    plugins: ['transform-object-rest-spread', 'babel-plugin-syntax-dynamic-import']
                }
            },
            include: [
                path.resolve(__dirname, "frontend/assets"),
                path.resolve(__dirname, "node_modules/url-regex")
            ]
        },
        {
            test: /\.scss$/,
            use: extractSass.extract({
                use: [{
                    loader: "css-loader"
                }, {
                    loader: "sass-loader"
                }],
                // use style-loader in development
                fallback: "style-loader"
            })
        }
        ]
    }
};
