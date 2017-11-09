/**
 * Modelo de datos de la colección RestrictedWord
 */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

mongoose.connect('mongodb://localhost/Maskay', { useMongoClient: true });

var restrictedword_schema = new Schema({
	word:{type:String, required: "La palabra restringida es obligatoria"}
});

var RestrictedWord = mongoose.model("RestrictedWord", restrictedword_schema);

module.exports.RestrictedWord = RestrictedWord;