/**
 * Modelo de datos de la colección Email
 */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

mongoose.connect('mongodb://localhost/Maskay', { useMongoClient: true });

var email_match = [/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,"El email no es válido"]

var email_schema = new Schema({
	email:{type:String,required: true, match: email_match},
	url_requested: {type: Schema.Types.ObjectId, ref: "Page"},
	status: String
});

var Email = mongoose.model("Email", email_schema);

module.exports.Email = Email;