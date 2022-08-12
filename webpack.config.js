/* eslint-disable import/no-nodejs-modules */
/* eslint-env node */

const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  mode: process.env.NODE_ENV ?? 'development',
  context: path.join(__dirname, 'static'),
  entry: {
    app: ['@babel/polyfill', './main'],
    styles: './less/base.less',
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        exclude: /(dist|node_modules)/,
        use: {
          loader: 'babel-loader',
          options: {cacheDirectory: true},
        },
      },
      {
        test: /\.less$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'less-loader'],
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, 'css-loader', 'style-loader'],
      },
      {
        test: /favicon\.png$/,
        type: 'asset/resource',
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: 'Freight',
      favicon: 'favicon.png',
      template: path.join(__dirname, '/templates/index.html'),
    }),
    new MiniCssExtractPlugin({
      filename: 'styles.[chunkhash].css',
      chunkFilename: '[id].css',
    }),
  ],
  resolve: {
    modules: ['node_modules'],
    extensions: ['.jsx', '.js', '.json'],
    alias: {
      app: path.join(__dirname, 'static'),
    },
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
    },
  },
  output: {
    path: path.join(__dirname, 'dist'),
    filename: '[name].[chunkhash].js',
    publicPath: '/static/',
    clean: true,
  },
  devtool: 'source-map',
  devServer: {
    port: 5001,
    compress: true,
    static: [path.join(__dirname, 'static')],
    historyApiFallback: {
      rewrites: [{from: /^\/.*$/, to: '/static/index.html'}],
    },
    client: {
      overlay: true,
    },
    proxy: {
      '/api/*': 'http://localhost:5002',
      '/auth/*': 'http://localhost:5002',
      '/webhooks/*': 'http://localhost:5002',
    },
  },
};
