1. Необходимо собрать информацию о вакансиях на вводимую должность (используем `input` или через аргументы получаем должность) с сайтов **_HH_** (`обязательно`) и/или **_Superjob_** (`по желанию`).<br><br>
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы). <br><br>
Получившийся список должен содержать в себе минимум:
- Наименование вакансии.
- Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта, цифры преобразуем к цифрам).
- Ссылку на саму вакансию.
- Сайт, откуда собрана вакансия.
- `По желанию` можно добавить ещё параметры вакансии (например, работодателя и расположение). 
>Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame через pandas. 
> 
Сохраните в json либо csv.