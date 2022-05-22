const currencies = ['USD', 'EUR', 'UAH', 'KZT'];
const rates = getCurrencies();

const formInput = document.querySelector('#input');
const formResult = document.querySelector('#result');
const formSelect = document.querySelector('#select');
const formElements = document.querySelectorAll('#badge')

async function getCurrencies () {
    // get currencies
    const response = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
    const data = await response.json();
    const result = await data;

    for (let i = 0; i < currencies.length; i += 1) {
        let cur = currencies[i];
        rates[cur] = result['Valute'][cur];
    }

    // draw badges
    for (let i = 0; i < formElements.length; i += 1) {
        let el_cur_name = formElements[i].getAttribute('data-value');
        let cur_value = rates[el_cur_name]['Value']
        let cur_prev = rates[el_cur_name]['Previous']

        formElements[i].textContent = cur_value.toFixed(2);

        if (cur_value > cur_prev) {
            formElements[i].classList.add('badge-success');
        } else {
            formElements[i].classList.add('badge-warning');
        }
    }
}

function convertValue() {
    formResult.value = ((parseFloat(formInput.value) / rates[formSelect.value]['Value']) *
        rates[formSelect.value]['Nominal']).toFixed(2);
}

formInput.oninput = convertValue;
formSelect.oninput = convertValue;
