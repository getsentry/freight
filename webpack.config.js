/*eslint-env node*/

const path = require("path");
const webpack = require("webpack");
const ExtractTextPlugin = require("extract-text-webpack-plugin");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  context: path.resolve(__dirname, "static"),
  entry: {
    styles: "./less/base.less",
    app: "./main.jsx",
    vendor: "./vendor.js",
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        loader: "babel-loader",
        query: {
          presets: ["es2015", "react"]
        }
      },
      {
        test: /\.less$/,
        loader: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: "css-loader!less-loader"
        })
      },
      {
        test: /\.css$/,
        loader: ExtractTextPlugin.extract({
          fallback: "style-loader",
          use: "css-loader!less-loader"
        })
      },
      // inline base64 URLs for <=8k images, direct URLs for the rest
      {
        test: /\.(png|jpg)$/,
        loader: "url-loader",
        query: {
          limit: 8192
        }
      }
    ]
  },
  plugins: [
    new ExtractTextPlugin("styles.css"),
    new webpack.optimize.CommonsChunkPlugin({
      name: "vendor",
      filename: "vendor.js",
      minChunks: function (module) {
        return module.context && module.context.indexOf("node_modules") !== -1;
      }
    }),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
    }),
    new CopyWebpackPlugin([
      {
        from: "favicon.png"
      },
    ])
  ],
  resolve: {
    extensions: [".jsx", ".js", ".json"]
  },
  output: {
    publicPath: "/dist/",
    path: path.join(__dirname, "/dist"),
    filename: "[name].js",
  },
  devtool: "source-map",
  externals: {
    'react/addons': true,
  }
};
