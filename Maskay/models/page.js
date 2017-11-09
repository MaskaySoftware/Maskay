/**
 * Modelo de datos de la colección Page
 */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

mongoose.connect('mongodb://localhost/Maskay', { useMongoClient: true });

var page_schema = new Schema({
	url:String,
	date_analysis: Date,
	duration: Number,
	status: String
});

var Page = mongoose.model("Page", page_schema);

module.exports.Page = Page;