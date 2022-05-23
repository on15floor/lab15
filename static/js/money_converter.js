const formBadges = document.querySelectorAll('#badge');
const formCurrencies = document.querySelectorAll('#currencie');
const buffer = {};
const currencies = ['RUB', 'USD', 'EUR', 'UAH', 'KZT', 'TRY', 'AMD'];
const rates = getCurrencies();

async function getCurrencies () {
    // get currencies
    const response = await fetch('https://www.cbr-xml-daily.ru/daily_json.js');
    const data = await response.json();
    const result = await data;

    for (let i = 0; i < currencies.length; i += 1) {
        let cur_name = currencies[i];
        rates[cur_name] = result['Valute'][cur_name];
    }
    rates['RUB'] = {'Value': 1, 'Nominal': 1};  // a litle of hardcode here

    // draw badges
    for (let i = 0; i < formBadges.length; i += 1) {
        let cur_name = formBadges[i].getAttribute('data-value');
        if (cur_name === 'RUB') {
            continue;
        }

        let cur_value = rates[cur_name]['Value']
        let cur_prev = rates[cur_name]['Previous']

        formBadges[i].textContent = cur_value.toFixed(2);

        if (cur_value > cur_prev) {
            formBadges[i].classList.add('badge-success');
        } else {
            formBadges[i].classList.add('badge-warning');
        }
    }
}

function convertValue() {
    let obj_target = {};
    for (let i = 0; i < formCurrencies.length; i += 1) {
        let obj = formCurrencies[i];
        let cur_name = obj.getAttribute('data-value');

        if (obj.value === buffer[cur_name]) {
            continue;
        }

        buffer[cur_name] = obj.value;
        obj_target = obj;
        break;
    }

    let obj_target_cur_name = obj_target.getAttribute('data-value');
    let res_in_rub = ((parseFloat(obj_target.value) *
        rates[obj_target_cur_name]['Value']) /
        rates[obj_target_cur_name]['Nominal']).toFixed(2);

    for (let i = 0; i < formCurrencies.length; i += 1) {
        let obj = formCurrencies[i];
        let obj_cur_name = obj.getAttribute('data-value');

        if (obj_cur_name === obj_target_cur_name) {
            obj.value = obj_target.value;
            continue;
        }

        if (obj_cur_name === 'RUB') {
            obj.value = res_in_rub;
            buffer['RUB'] = res_in_rub;
            continue;
        }

        let obj_value= ((parseFloat(res_in_rub) /
            rates[obj_cur_name]['Value']) *
            rates[obj_cur_name]['Nominal']).toFixed(2);
        obj.value = obj_value
        buffer[obj_cur_name] = obj_value
    }
}

for (let i = 0; i < formCurrencies.length; i += 1) {
    let cur = formCurrencies[i].getAttribute('data-value');
    buffer[cur] = ''
    formCurrencies[i].oninput = convertValue;
}
