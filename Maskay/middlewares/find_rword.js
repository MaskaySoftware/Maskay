/**
 * Middleware para la búsqueda de una palabra
 */

var RestrictedWord = require("../models/restricted_word").RestrictedWord;

module.exports = function(req, res, next){
	RestrictedWord.findById(req.params.id,function(err, word){
		if(word != null){
			res.locals.restricted_word = word;
			next();
		}else{
			res.redirect("/maskay/admin");
		}
	});
}