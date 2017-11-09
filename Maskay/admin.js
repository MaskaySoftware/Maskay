/**
 * Archivo de configuración principal de la interfaz del admin
 */

var express = require("express");
var RestrictedWord = require("./models/restricted_word").RestrictedWord;
var find_rword_middleware = require("./middlewares/find_rword")
var router = express.Router();

router.get("/",function(req,res){
	res.redirect("admin/restricted_word");
});

router.route('/logout') 
	.get(function(req, res) { 
	req.session.destroy(function(err){
        if(err){
            console.log(err);
        } else {
            res.redirect('/maskay');
        }
    });
})

/* REST */

router.get("/restricted_word/new",function(req, res){
	res.render("admin/restricted_word/new");
});

router.all("/restricted_word/:id*",find_rword_middleware);

router.get("/restricted_word/:id/edit",function(req, res){
	res.render("admin/restricted_word/edit");
});


router.route("/restricted_word/:id")
	.get(function(req,res){
		res.render("admin/restricted_word/show");
	})
	.put(function(req,res){
		res.locals.restricted_word.word = req.body.restricted_word;
		res.locals.restricted_word.save(function(err){
			if(!err){
				res.redirect("/maskay/admin");
			}else{
				res.render("/maskay/admin/restricted_word/" + req.params.id + "/edit");
			}
		});
	})
	.delete(function(req, res){
		RestrictedWord.findOneAndRemove({_id: req.params
			.id},function(err){
			if(!err){
				res.redirect("/maskay/admin")
			}else{
				console.log(err);
				res.redirect("/maskay/admin/restricted_word/"+req.params.id);
			}
		});
	});

router.route("/restricted_word")
	.get(function(req, res){
		RestrictedWord.find({},function(err, words){
			if(err){
				res.redirect("/maskay/admin");
				return;
			}
			res.render("admin/restricted_word/index",{words: words});
		});
	})
	.post(function(req, res){
		var data = {
			word: req.body.restricted_word
		};

		var restrictedWord = new RestrictedWord(data);

		restrictedWord.save(function(err, word){
			if(!err){
				res.redirect("/maskay/admin");
			}else{
				res.render(err);
			}
		});
	});

module.exports = router;