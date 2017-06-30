/*eslint-env node*/

var path = require("path"),
    webpack = require("webpack");
var ExtractTextPlugin = require("extract-text-webpack-plugin");
var CopyWebpackPlugin = require('copy-webpack-plugin');

module.exports = {
  context: __dirname + "/static",
  entry: {
    "styles": "./less/base.less",
    "app": "./main",
    "vendor": [
      "ansi_up",
      "babel-core/polyfill",
      "jquery",
      "moment",
      "react-router"
    ]
  },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        loader: "babel-loader"
      },
      {
        test: /\.json$/,
        loader: "json-loader"
      },
      {
        test: /\.less$/,
        loader: ExtractTextPlugin.extract("style-loader", "css-loader!less-loader")
      },
      {
        test: /\.css$/,
        loader: ExtractTextPlugin.extract("style-loader", "css-loader")
      },
      // inline base64 URLs for <=8k images, direct URLs for the rest
      {
        test: /\.(png|jpg)$/,
        loader: "url-loader?limit=8192"
      }
    ]
  },
  plugins: [
    function() {
      this.plugin("done", function(stats) {
        var app = stats.toJson({
          assetsSort: true
        }).assetsByChunkName.app[0]

        var vendor = stats.toJson({
          assetsSort: true
        }).assetsByChunkName.vendor[0]

        var styles = stats.toJson({
          assetsSort: true
        }).assetsByChunkName.styles[0]

        var newObj = {
          "assets": {
            "vendor.js": vendor,
            "app.js": app,
            "styles.css": styles
          },
          "publicPath": "/static/"
        };
        console.log(newObj)
        require("fs").writeFileSync(
          path.join(__dirname, "/", "stats.json"),
          JSON.stringify(newObj));
      });
    },
    new ExtractTextPlugin("styles.css", {
      allChunks: true
    }),
    new webpack.optimize.DedupePlugin(),
    new webpack.ProvidePlugin({
        $: 'jquery',
        jQuery: 'jquery',
    }),
    new CopyWebpackPlugin([
        {from: 'favicon.png'},
    ])
  ],
  resolve: {
    modulesDirectories: ["node_modules"],
    extensions: ["", ".jsx", ".js", ".json"]
  },
  output: {
    publicPath: "/dist/",
    path: __dirname + "/dist",
    filename: "[name].[chunkhash].js",
  },
  devtool: 'source-map'
};
