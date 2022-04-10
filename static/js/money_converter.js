// Объект с курсами валют
const rates = {};
// Элементы для отображения курсов валют
const elementUSD = document.querySelector('[data-value="USD"]');
const elementEUR = document.querySelector('[data-value="EUR"]');
const elementUAH = document.querySelector('[data-value="UAH"]');
const elementKZT = document.querySelector('[data-value="KZT"]');
// Элементы формы
const input = document.querySelector('#input');
const result = document.querySelector('#result');
const select = document.querySelector('#select');

// Функция получения и отображения курсов валют

async function getCurrencies () {
    // Получаем последние курсы валют
    const response = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
    const data = await response.json();
    const result = await data;

    // Парсим интересующие нас курсы валют
    rates.USD = result.Valute.USD;
    rates.EUR = result.Valute.EUR;
    rates.UAH = result.Valute.UAH;
    rates.KZT = result.Valute.KZT;

    // Заполняем шаблон текущим курсом
    elementUSD.textContent = rates.USD.Value.toFixed(2);
    elementEUR.textContent = rates.EUR.Value.toFixed(2);
    elementUAH.textContent = rates.UAH.Value.toFixed(2);
    elementKZT.textContent = rates.KZT.Value.toFixed(2);

    // Подкрашиваем курс, в зависимости от того вырос он или нет за сутки
    if (rates.USD.Value > rates.USD.Previous) {
        elementUSD.classList.add('badge-success');
    } else {
        elementUSD.classList.add('badge-warning');
    }
    if (rates.EUR.Value > rates.EUR.Previous) {
        elementEUR.classList.add('badge-success');
    } else {
        elementEUR.classList.add('badge-warning');
    }
    if (rates.UAH.Value > rates.UAH.Previous) {
        elementUAH.classList.add('badge-success');
    } else {
        elementUAH.classList.add('badge-warning');
    }
    if (rates.KZT.Value > rates.KZT.Previous) {
        elementKZT.classList.add('badge-success');
    } else {
        elementKZT.classList.add('badge-warning');
    }
}

// Функция конвертации курса валют
function convertValue() {
    result.value = ((parseFloat(input.value) / rates[select.value].Value) *
        rates[select.value].Nominal).toFixed(2);
}

getCurrencies();
//setInterval(getCurrencies, 10000);

input.oninput = convertValue;
select.oninput = convertValue;