function playGame() {
    var player1Dice = document.getElementById('player1Dice');
    var player2Dice = document.getElementById('player2Dice');
    var resultElement = document.getElementById('result');

    // Roll dice for each player
    var player1Roll = rollDice(player1Dice);
    var player2Roll = rollDice(player2Dice);

    // Display the result
    var result = determineWinner(player1Roll, player2Roll);
    resultElement.textContent = result;
}

function rollDice(diceElement) {
    var randomNumber = Math.floor(Math.random() * 6) + 1;

    // You can customize the dice faces as needed
    var diceFaces = ['⚀', '⚁', '⚂', '⚃', '⚄', '⚅'];

    diceElement.textContent = diceFaces[randomNumber - 1];

    return randomNumber;
}

function determineWinner(player1Roll, player2Roll) {
    if (player1Roll > player2Roll) {
        return 'Player 1 wins!';
    } else if (player1Roll < player2Roll) {
        return 'Player 2 wins!';
    } else {
        return 'It\'s a tie!';
    }
}
