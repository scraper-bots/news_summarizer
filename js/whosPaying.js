function whosPaying(names) {
    var numOfPeople = names.length;
    var randomIndex = Math.floor(Math.random() * numOfPeople);
    var selectedPerson = names[randomIndex];
    return selectedPerson + " is going to buy lunch today!";
}

