/**
 * Archivo de configuración principal del componente de la interfaz
 */


// Variables

var directory = "maskay";
var puerto = 7080;
var express = require("express");
var async = require('async');
var bodyParser = require("body-parser");
var app = express();
var spawn = require('child_process').spawn,
	pages = '',
	py    = spawn('python', ['main.py']),
	result = '';
var timeout = require("connect-timeout");
var URL = require("url");
var Admin = require("./models/admin").Admin;
var Page = require("./models/page").Page;
var Email = require("./models/email").Email;
var Document = require("./models/document").Document;
var exec = require('child_process').exec, spider;
var spawn = require('child_process').spawn;
var session = require("express-session");
var router_app = require("./admin");
var session_middleware = require("./middlewares/session");
var methodOverride = require("method-override");
var RedisStore = require("connect-redis")(session);
app.use(timeout('10000s'));
app.use(haltOnTimedout);
var sessionMiddleware = session({
	store: new RedisStore({}),
	secret:"secretpassmaskay",
	saveUninitialized: false,
    resave: false
});
app.use(sessionMiddleware);
app.use('/',express.static('./public'));
app.use('/' + directory,express.static('./public'));
app.use(bodyParser.json()); // Para peticiones application/json
app.use(bodyParser.urlencoded({extended: false}));
app.set("view engine","jade");
app.use(methodOverride("_method"));
app.use("/" + directory + "/admin",session_middleware);
app.use("/" + directory + "/admin",router_app);
app.use(function(err, req, res, next) {
	console.log(err.stack);
});

// Se exponen las interfaces 
// Index
app.get("/" + directory + "/",function(req, res){
	res.render("index");
});
// Login
app.get("/" + directory + "/login",function(req, res){
	res.render("login");
});
// Autenticación
app.post("/" + directory + "/login",function(req, res){
	Admin.findOne({email:req.body.email, password: req.body.password},function(err, admin){
		if(admin == null){
			res.redirect("/" + directory + "/login");
		}else{
			req.session.admin_id = admin._id;
			res.redirect("/" + directory + "/admin");
		}
	});
});
// Guardar email
app.post("/" + directory + "/email",function(req, res){
	var data = {
				email: req.body.email,
				url_requested: req.body.page,
				status: "not_sent"
			};
	var email = new Email(data);
	email.save(function(err, email){
		if(!err){
			ls = spawn('python',["main_correo.py", req.body.page],{stdio: 'ignore',detached: true}).unref();
			res.render("mensaje");
		}else{
			res.render(err);
		}
	});
});
// Búscar
app.post("/" + directory + "/buscar",function(req,res){
	// Ejecutamos la araña para obtener los primerso links
	req.setTimeout(0) // no timeout
	var str = req.body.pagina;
	if (!str.startsWith("http://") && !str.startsWith("https://")){
		str = "http://" + str;
	}
	if(isValidUrl(str, 1,0)){
		var urlP = URL.parse(str);
		var url_parse = urlP.protocol + "//" + urlP.hostname;
		Page.findOne({url: url_parse},function(err, page){
			if(err) res.redirect("/" + directory + "/");
			if(page == null){
				spider = exec('scrapy crawl spider_first -a url_to=' + str,
					function (error, stdoutput, stderror) {
					var data = {
						url: url_parse,
						date_analysis: new Date(),
						status: "Searching"
					};

					var page = new Page(data);

					page.save(function(err, page){
						if(!err){
							res.render("email", {"page" : page});
						}else{
							res.render(err);
						}
					});
					pages = JSON.parse(stdoutput);
					if(pages.length > 4){
						page2 = pages[Math.round((1/2)*pages.length)];
						page3 = pages[Math.round((1/4)*pages.length)];
						page4 = pages[Math.round((3/4)*pages.length)];
						ls = spawn('python',["main_search.py", str , page2 , page3 , page4 ],{stdio: 'ignore',detached: true}).unref();
					}else{
						ls = spawn('python',["main_search.py", str],{stdio: 'ignore',detached: true}).unref();
					}
					
				});
			}else if(page.status == 'Searching'){
				res.render("email", {"page" : page});
			}else{
				Document.find({url_extraccion: url_parse},function(err, docs){
					if(err){
						res.redirect("/" + directory + "/");
						return;
					}
					if (docs.length == 0){
						res.render("index", {err_mensaje: "Lo sentimos, la página que intenta buscar no ha podido ser analizada correctamente por motivos de seguridad."});
						return;
					}else{
						var startTime = new Date();
						pdfimg = req.body.pdf_img ? true : false
						python = exec("python main.py '" + str + "' '" + req.body.buscar + "' " + pdfimg,{maxBuffer: 1024 * 1000},function(err, stdout, stderr){
							if(err){ console.log(err); }
							else{
								documents = JSON.parse(stdout);
								documents.sort(function(a,b){
									if (a[2] < b[2])
										return 1;
									if (a[2] > b[2])
										return -1;
									return 0;
								})
								var endTime = new Date();
								console.log("Url: " + url_parse + " Tiempo : " + returnDiffToText(endTime-startTime));
								res.render("buscar", {"documents" : documents, "buscar": req.body.buscar, "pagina": str });
							}
						});

					}
				});
			}
		});
	}else{
		res.render("index", {err_mensaje: "Lo sentimos, la página que ingreso no es una URL válida."});
		return;
	}
});

/**
 * Función a ejecutar si el tiempo de respuesta se excede.
 * Recibe
 * - request Petición
 * - response Respuesta
 * - next Siguiente función a ejecutar
 */
function haltOnTimedout(req, res, next){
	if (!req.timedout) next();
}

/**
 * Función que devuelve el tiempo transcurrido en dias, horas, minutos y segundos
 * Recibe
 * - milisegundos Tiempo transcurrido en milisegundos
 * Devuelve String
 */
function returnDiffToText(timeDiff)
{
    // obtenemos los segundos
    var timeDiff = timeDiff / 1000;
 
    var result="";
    if(timeDiff<60)
    {
        // unicamente mostraremos los segundos
        result=timeDiff+" segundos";
    }else{
        // cogemos la parte entera de los segundos
        var seconds = Math.round(timeDiff % 60);
 
        // restamos los segundos que hemos cogido
        timeDiff = Math.floor(timeDiff / 60);
 
        // cogemos los minutos
        var minutes = Math.round(timeDiff % 60);
 
        // restamos los minutos que hemos cogido
        timeDiff = Math.floor(timeDiff / 60);
 
        // cogemos las horas
        var hours = Math.round(timeDiff % 24);
 
        // restamos las horas que hemos cogido
        timeDiff = Math.floor(timeDiff / 24);
 
        // el resto, son dias
        var days = timeDiff;
 
        if(days>0)
        {
            result=days+" dias, "+hours+" horas, "+minutes+" minutos y "+seconds+" segundos";
        }else if(hours>0){
            result=hours+" horas, "+minutes+" minutos y "+seconds+" segundos";
        }else{
            result=minutes+" minutos y "+seconds+" segundos";
        }
    }
    return result;
}

/**
 * Tiene que recibir:
 *  - la url a revisar
 *  - indicar si es obligatorio [1|0]. Si es obligatorio, devuelve
 *    false si la url esta vacia
 *  - indicar si validamos que la direccion pueda ser de un servidor
 *    ftp [1|0]
 * Devuelve True o False
 */
function isValidUrl(url,obligatory,ftp)
{
    // Si no se especifica el paramatro "obligatory", interpretamos
    // que no es obligatorio
    if(obligatory==undefined)
        obligatory=0;
    // Si no se especifica el parametro "ftp", interpretamos que la
    // direccion no puede ser una direccion a un servidor ftp
    if(ftp==undefined)
        ftp=0;
 
    if(url=="" && obligatory==0)
        return true;
 
    if(ftp)
        var pattern = /^(http|https|ftp)\:\/\/[a-z0-9\.-]+\.[a-z]{2,4}/gi;
    else
        var pattern = /^(http|https)\:\/\/[a-z0-9\.-]+\.[a-z]{2,4}/gi;
 
    if(url.match(pattern))
        return true;
    else
        return false;
}

// Se inicia la aplicación en el puerto indicado
app.listen(puerto);

