/**
 * Middleware para la autenticación del usuario administrador
 */

var Admin = require("../models/admin").Admin;

module.exports  = function(req, res, next){
	if(!req.session.admin_id){
		res.redirect("/maskay/login");
	}else{
		Admin.findById(req.session.admin_id,function(err,admin){
			if(err){
				console.log(err);
				res.redirect("/maskay/login");
			}
			else{
				res.locals = { admin: admin };
				next();
			}
		});
	}
}