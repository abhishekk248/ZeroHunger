const express=require("express");
const https=require("https");
const mysql = require('mysql2');
const bodyParser=require("body-parser");

const app=express();
app.use(bodyParser.urlencoded({extended:true}));
app.use(express.static('public'));
app.get("/",function(req,res){
    res.sendFile(__dirname+"/homepage.html"); 
});

 app.post("/login",function(req,res){
    const uname=req.body.username;
    const pwd=req.body.password;
    const connection = mysql.createConnection({
        host: 'localhost',
        user: 'root',
        password: 'abhishek',
        database: 'Zero_Hunger'
    });
    connection.connect((error) => {
        if (error) {
          console.error('Error connecting to MySQL database:', error);
        } else {
          console.log('Connected to MySQL database!');
        }
    });
    connection.query('SELECT * FROM credentials', function(err, rows, fields) {
        if (err) throw err;
        
        for (var i = 0; i < rows.length; i++) {
            console.log(rows);
            if (rows[i].username==uname && rows[i].password==pwd){
                console.log("came here");
            }
        }
        res.sendFile(__dirname+"/homepage2.html");
    });
      // close the MySQL connection
    connection.end();
});
app.post("/signup",function(req,res){
    const uname=req.body.name;
    const pwd=req.body.password;
    const email=req.body.email;
    const uniqueNumber = new Date().getTime();
    const connection = mysql.createConnection({
        host: 'localhost',
        user: 'root',
        password: 'abhishek',
        database: 'Zero_Hunger'
    });
    connection.connect(function(err) {
        if (err) throw err;
        console.log("Connected!");
        var sql = "INSERT INTO credentials (userID,username,password,emailID) VALUES ({uniqueNumber},{uname},{pwd},{email})";
        connection.query(sql, function (err, result) {
          console.log("1 record inserted");
          alert("registered successfully");
        });
    });
      // close the MySQL connection
    connection.end();
    
    res.sendFile(__dirname+"/homepage.html");
});
app.get("/sign",function(req,res){
    res.sendFile(__dirname+"/signup.html");
});
app.post("/",function(req,res){

});

app.listen(3000,function(){
    console.log("Running on 3000");
});