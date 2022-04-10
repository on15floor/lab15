##### SQL

---
##### Работа с таблицами
**Создание**  
`CREATE TABLE` book(  
book_id `INT PRIMARY KEY AUTO_INCREMENT`,  
title `VARCHAR(50)`,  
author `VARCHAR(30)`,  
price `DECIMAL(8, 2)`,  
amount `INT`);  

**Занесение**  
`INSERT INTO` book (title, author, price, amount)  
`VALUES` ('Белая гвардия', 'Булгаков М.А.', 540.50, 5);  

**Добавление записей из другой таблицы**  
`INSERT INTO` book (title, author, price, amount)  
`SELECT` title, author, price, amount  
`FROM` supply;

**Запросы на обновление**  
`UPDATE` таблица `SET` поле1 = выражение1, поле2 = выражение2;  
**Запросы на удаление**  
`DELETE` FROM таблица;
---
##### Работа с таблицами
`SELECT` * `FROM` book; *----Выборка всех данных из таблицы*  
`SELECT` title `AS` Название, amount `FROM` book; *----Выборка отдельных столбцов*  
`SELECT` title, price, (price * 18/100)/(1+18/100) `AS` tax `FROM` book; *----Вычисляемые столбцы*  
`SELECT` title, amount, price, `IF`(amount<4, price * 0.5, price * 0.7) `AS` sale `FROM` book; *----Логические функции IF*  	
`SELECT` title, price `FROM` book `WHERE` price < 600; *----Выборка по условию WHERE*  
`SELECT` title, author, price `FROM` book `WHERE` price > 600 `AND` author = 'Булгаков М.А.'; *----Логические операции*  	
`SELECT` title, amount `FROM` book `WHERE` amount `BETWEEN` 5 `AND` 14; *----Операторы BETWEEN*  
`SELECT` title, amount `FROM` book `WHERE` author `IN` ('Булгаков М.А.', 'Достоевский Ф.М.'); *----Операторы IN*  
`SELECT` title `FROM` book `WHERE` title `LIKE` 'Б%'; *----Оператор LIKE*  
`SELECT` title, author, price `FROM` book `ORDER BY` title `DESC`; *----Сортировка DESC (по убыванию)*  
`SELECT` title, author, price `FROM` book `ORDER BY` 1 `ASC`; *----Сортировка ASC (по возрастанию)*  
`SELECT DISTINCT` author `FROM` book; *----Выбор уникальных элементов столбца*  
`SELECT` author, `COUNT`(author), `SUM`(amount), `COUNT`( * ) `FROM` book `GROUP BY` author; *----Групповые функции SUM и COUNT*  
`SELECT` author, `MIN`(price) `AS` min_price `FROM` book `GROUP BY` author; *----Групповые функции MIN, MAX и AVG*  
---
**Групповые функции, выборка данных по условию**  
`SELECT` author, `MIN`(price) `AS` Минимальная_цена, `MAX`(price) `AS` Максимальная_цена  
`FROM` book `GROUP BY` author `HAVING SUM`(price * amount) > 5000;  
**Групповые функции, WHERE и HAVING (после GROUP BY)**  
`SELECT` author, `MIN`(price) `AS` Минимальная_цена, `MAX`(price) `AS` Максимальная_цена  
`FROM` book `WHERE` author <> 'Есенин С.А.' `GROUP BY` author `HAVING SUM`(amount) > 10;
