/*eslint-env node*/

const path = require("path"),
      webpack = require("webpack");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyWebpackPlugin = require('copy-webpack-plugin');
const CleanWebpackPlugin = require('clean-webpack-plugin');
const ManifestPlugin = require('webpack-manifest-plugin');



module.exports = {
  context: __dirname + "/static",
  entry: {
    "styles": "./less/base.less",
    "app": "./main",
    "vendor": [
      "ansi_up",
      "babel-polyfill",
      "jquery",
      "moment",
      "react-router"
    ]
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
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          "less-loader",
        ]
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          "css-loader",
          "style-loader",
        ]
      },
      // inline base64 URLs for <=8k images, direct URLs for the rest
      {
        test: /\.(png|jpg)$/,
        use: {
          loader: 'url-loader',
          options: {
            limit: 8192,
          }
        }
      }
    ]
  },
  plugins: [
    new CleanWebpackPlugin(),
    new ManifestPlugin({
      fileName: '../stats.json',
      publicPath: '',
      basePath: '',
      generate: (seed, files) => ({
        assets: files.reduce((manifest, {name, path}) => ({...manifest, [name]: path}), seed),
        publicPath: '/static/',
      })
    }),
		new MiniCssExtractPlugin({
			filename: 'styles.[chunkhash].css',
			chunkFilename: "[id].css",
			allChunks: true,
		}),
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
    }),
    new CopyWebpackPlugin([
        {from: 'favicon.png'},
    ])
  ],
  resolve: {
    modules: ["node_modules"],
    extensions: [".jsx", ".js", ".json"]
  },
  output: {
    publicPath: "/dist/",
    path: __dirname + "/dist",
    filename: "[name].[chunkhash].js",
  },
  devtool: 'source-map'
};
