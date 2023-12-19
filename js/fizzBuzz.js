var out = [];

function fizBuzz() {
    for (var i = 1; i <= 100; i++) {
        if (i % 3 === 0 && i % 5 === 0) {
            out.push("FizzBuzz");
        } else if (i % 3 === 0) {
            out.push("Fizz");
        } else if (i % 5 === 0) {
            out.push("Buzz");
        } else {
            out.push(i);
        }
    }
}

fizBuzz();

console.log(out);
