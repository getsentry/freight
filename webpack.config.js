/* eslint-env node */

const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
  context: __dirname + '/static',
  entry: {
    styles: './less/base.less',
    app: ['@babel/polyfill', './main'],
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
        test: /favicon.png$/,
        use: {
          loader: 'file-loader',
          options: {
            publicPath: 'static',
            outputPath: 'dist',
          },
        },
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      title: 'Freight',
      favicon: 'favicon.png',
      template: path.join(__dirname + '/templates/index.html'),
    }),
    new CleanWebpackPlugin(),
    new MiniCssExtractPlugin({
      filename: 'styles.[chunkhash].css',
      chunkFilename: '[id].css',
      allChunks: true,
    }),
  ],
  resolve: {
    modules: ['node_modules'],
    extensions: ['.jsx', '.js', '.json'],
  },
  optimization: {
    splitChunks: {
      chunks: 'all',
    },
  },
  output: {
    publicPath: '/static/',
    path: path.join(__dirname, 'dist'),
    filename: '[name].[chunkhash].js',
  },
  devtool: 'source-map',
  devServer: {
    contentBase: false,
    compress: true,
    // index: '/static/index.html',
    historyApiFallback: {
      index: '/static/',
    },
    overlay: true,
    port: 5001,
    proxy: {
      '/api/*': {
        target: 'http://localhost:5002',
      },
      '/auth/*': {
        target: 'http://localhost:5002',
      },
      '/webhooks/*': {
        target: 'http://localhost:5002',
      },
    },
  },
};
