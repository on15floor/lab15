// Найдем все объекты с классом changeTheme
let changeThemeButtons = document.querySelectorAll('.changeTheme');

// Слушаем кнопку переключения темы
changeThemeButtons.forEach(button => {
    button.addEventListener('click', function () {
        let theme = this.dataset.theme;
        applyTheme(theme);
    });
});

// Функция переключения css
function applyTheme(themeName) {
    document.querySelector('[title="theme"]').setAttribute('href', `/static/css/theme_${themeName}.css`);
    changeThemeButtons.forEach(button => {
        button.style.display = 'block';
    });
    document.querySelector(`[data-theme="${themeName}"]`).style.display = 'none';
    localStorage.setItem('theme', themeName);
}

// Определяем объект активной темы из ЛС
let activeTheme = localStorage.getItem('theme');
// Применяем соответствующий стиль из ЛК
if(activeTheme === null || activeTheme === 'dark') {
    applyTheme('dark');
} else if (activeTheme === 'light') {
    applyTheme('light');
}
