import express from "express";
import bodyParser from "body-parser";
import { dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const app = express();
const port = 3000;
const password = 'ILoveProgramming';
var userAuthenticated = false;

app.use(bodyParser.urlencoded({ extended: true }));

function checkPassword(req, res, next) {
  if (req.password === password) { 
    userAuthenticated= true;
  }
  next();
}
 
app.use(checkPassword);


app.get("/", (req, res) => {
  res.sendFile(__dirname + "/public/index.html");
});


app.post("/submit", (req, res) => {
  if (userAuthenticated) {
    res.sendFile(__dirname + "/public/secret.html");
  } else { 
      res.sendFile(__dirname + "/public/index.html");

  }

});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
