/**
 * Modelo de datos de la colección Admin
 */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

mongoose.connect('mongodb://localhost/Maskay', { useMongoClient: true });

var email_match = [/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/,"El email no es válido"]

var adminSchemaJSON = {
	name:String,
	email:{type:String,required: true, match: email_match},
	password: {type:String, required: true}
}

var admin_schema = new Schema(adminSchemaJSON);

var Admin = mongoose.model("Admin", admin_schema);

module.exports.Admin = Admin;