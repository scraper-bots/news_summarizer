
var buttonColours = ["red", "blue", "green", "yellow"];
var gamePattern = [];
var userChosenColour = "";
var userClickedPattern = [];
var level = 0;
var gameStarted = false;


$(document).keydown(clickDetector);
$(".btn").click(userChoice);

function nextSequence() {
  level++;
  $("#level-title").text("Level " + level);
  var randomNumber = Math.floor(Math.random() * 3);
  var randomChosenColour = buttonColours[randomNumber];
  flash(randomChosenColour);
  playSound(randomChosenColour);
}



function playSound(name_of_sound){ 
  var audio = new Audio("sounds/" + name_of_sound + ".mp3");
  audio.play();
}

function flash(name_of_color){
  gamePattern.push(name_of_color);
  $("#" + name_of_color).fadeIn(100).fadeOut(100).fadeIn(100);
}

function animatePress(currentColour) {
  $("#"+currentColour).addClass('pressed');
  setTimeout(() => {
    $("#"+currentColour).removeClass('pressed');
  }, 100);
}


function userChoice() {
  var userChosenColour = $(this).attr("id");
  userClickedPattern.push(userChosenColour);
  playSound(userChosenColour);
  animatePress(userChosenColour);
  checkAnswer(userClickedPattern.length - 1);

}

function clickDetector() {
  if (!gameStarted) {
    $("#level-title").text("Level " + level);
    nextSequence();
    gameStarted = true;
  }
}

function checkAnswer(currentLevel) {
  if (userClickedPattern[currentLevel] === gamePattern[currentLevel]) {
    console.log("Success"); 
    if (userClickedPattern.length === gamePattern.length) {
      setTimeout(function () {
        nextSequence();
        userClickedPattern = []; 
      }, 1000);
    }
  } else {
    console.log("Wrong"); 
  }
}