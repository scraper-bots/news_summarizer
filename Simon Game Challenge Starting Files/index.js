
var buttonColours = ["red", "blue", "green", "yellow"];
var gamePattern = [];
var userClickedPattern = [];


$(".btn").click(function() {
  var userChosenColour = $(this).attr("id");
  userClickedPattern.push(userChosenColour);
});


function nextSequence() { 
  
  var randomNumber = Math.floor(Math.random() * 3);
  var randomChosenColour = buttonColours[randomNumber];
  
   flash(randomChosenColour);
  playSound(randomChosenColour);
}




playSound(name_of_sound){ 
  var audio = new Audio("sounds/" + name_of_sound + ".mp3");
  audio.play();
}

flash(name_of_color){
  gamePattern.push(name_of_color);
  $("#" + name_of_color).fadeIn(100).fadeOut(100).fadeIn(100);
}

function animatePress(currentColour) {
  $("#"+currentColour).addClass('pressed');
  setTimeout(() => {
    $("#"+currentColour).removeClass('pressed');
  }, 100);
}
