let snowflakesCount = 50;
let bodyHeightPx = document.body.offsetHeight;
let pageHeightVH = (100 * bodyHeightPx / window.innerHeight);

function spawnSnow(snowDensity = 200) {
    snowDensity -= 1;

    for (let x = 0; x < snowDensity; x++) {
        let board = document.createElement('div');
        board.className = "snowflake";

        document.getElementById('snow').appendChild(board);
    }
}

function addCss(rule) {
    let css = document.createElement('style');
    css.appendChild(document.createTextNode(rule)); // Support for the rest
    document.getElementsByTagName("head")[0].appendChild(css);
}

function randomInt(value = 100){
    return Math.floor(Math.random() * value) + 1;
}

function randomRange(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function spawnSnowCSS(snowDensity = 200){
    let snowflakeName = "snowflake";
    let rule = ``;

    for(let i = 1; i < snowDensity; i++){
        let randomX = Math.random() * 100; // vw
        let randomOffset = randomRange(-100000, 100000) * 0.0001; // vw;
        let randomXEnd = randomX + randomOffset;
        let randomXEndYoyo = randomX + (randomOffset / 2);
        let randomYoyoTime = randomRange(30000, 80000) / 100000;
        let randomYoyoY = randomYoyoTime * pageHeightVH; // vh
        let randomScale = Math.random();
        let fallDuration = randomRange(10, pageHeightVH / 10 * 3); // s
        let fallDelay = randomInt(pageHeightVH / 10 * 3) * -1; // s
        let opacity = Math.random();

        rule += `
        .${snowflakeName}:nth-child(${i}) {
            opacity: ${opacity};
            transform: translate(${randomX}vw, -10px) scale(${randomScale});
            animation: fall-${i} ${fallDuration}s ${fallDelay}s linear infinite;
        }

        @keyframes fall-${i} {
            ${randomYoyoTime*100}% {
                transform: translate(${randomXEnd}vw, ${randomYoyoY}vh) scale(${randomScale});
            }

            to {
                transform: translate(${randomXEndYoyo}vw, ${pageHeightVH}vh) scale(${randomScale});
            }
            
        }
        `
    }
    addCss(rule);
}

window.onload = function() {
    spawnSnowCSS(snowflakesCount);
    spawnSnow(snowflakesCount);
};
