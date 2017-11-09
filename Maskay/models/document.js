/**
 * Modelo de datos de la colección Document
 */

var mongoose = require('mongoose');
var Schema = mongoose.Schema;

mongoose.connect('mongodb://localhost/Maskay', { useMongoClient: true });

var documentSchemaJSON = {
	num_visitas : Number,
    fecha_creacion : Date,
    url_pdf : String,
    ana_img : Number,
    url_extraccion : String,
    ana_text : Number,
    nombre : String
}

var document_schema = new Schema(documentSchemaJSON);

var Document = mongoose.model("Document", document_schema);

module.exports.Document = Document;