# Отчет о выполнении проекта по дисциплине "Программная инженерия кибериммунных систем" по теме "Cистема управления кардиостимулятором с интерфейсом удалённого доступа"

- [Постановка задачи](#постановка-задачи)
- [Определение ценностей продукта и негативных событий](#определение-ценностей-продукта-и-негативных-сценариев)
- [Роли и пользователи](#роли-и-пользователи)
- [Цели и предположения безопасности](#цели-и-предположения-безопасности)
- [Диаграмма контекста](#диаграмма-контекста)
- [Базовые сценарии](#базовые-сценарии)
- [Оновные блоки](#основные-блоки)
- [Архитектура](#архитектура)
- [Базовый сценарий и HLA](#базовый-сценарий-и-HLA)
- [Негативные сценарии](#негативные-сценарии)
- [Политика архитектуры](#политика-архитектуры)
- [Тесты](#тесты)

## Постановка задачи
Построение безопасной архитектуры и прототипа системы управления кардиостимулятором (ЭКС) с интерфейсом удалённого доступа.

Удаленный интерфейс доступа к ЭКС основан на коммерческой технологии Home Monitoring BIOTRONIK,
суть которой заключается в установлении телеметрической связи между ЭКС и прибором пациента “Cardiomessenger” (на базе модифицированного мобильного телефона) для создания единой замкнутой коммуникационной системы «устройство – “Cardiomessenger” – сервисный центр BIOTRONIK – лечащий врач – пациент».
Устройство пользовательского интерфейса способно принимать данные с ЭКС и передавать их в мед. учреждение, также мы добавили возможность вызова неотложной помощи в случае ухудшения состояния пациента.

## Определение ценностей продукта и негативных сценариев
| Ценность | Негативные события | Величина ущерба | Комментарий |
|:----------:|:----------:|:----------:|:----------:|
| Пациент | Причинение тяжкого вреда здоровью или летальный исход | Высокий | Судебные иски |
| Информация с ЭКС | Причинение ущерба | Высокий | Нарушение данных приведет к неправильной оценке состояния пациента |
| ЭКС | Выход из строя | Средний | Потребуется обращение в медицинскую организацию в срочном порядке |

## Роли и пользователи
| Роль | Описание |
|:----------:|:----------:|
| Пациент | Использование ЭКС |
| Кардиолог | Настройка ЭКС |

## Цели и предположения безопасности
### Цели безопасности
1. Выполняются команды только от аутентичных и авторизованных пользователей.
2. Команды, которые отвечают за стимуляцию сердца, не причиняют вред здоровью пациента.
3. Доступ к конфиденциальной информации ЭКС имеют только аутентичные и авторизованные пользователи.
4. Временные показатели частоты сердечного ритма и другая информация о состоянии пациента, хранящаяся в библиотеке данных, достоверны и не противоречивы.

### Предположения безопасности
1. Данные, получаемые с датчиков ЭКС, достоверны.
2. Лечащий врач благонадежен.
3. Программатор ЭКС благонадежен.
4. Устройство для взаимодействия с пользователем благонадежно.

#### Дополгительные меры защиты
Узнать, достоверны ли данные с датчиков можно, если мы видим, что сердце посылает нам электрический сигнал после того, как совершило удар менее чем 200 мс назад, это доказывает, что нас обманули по поводу предыдущего удара пульса. Если подобное имеет место, значит, мы получаем преднамеренные электромагнитные помехи.

Также, чтобы проверить наличие вируса в ПО, можно изучить энергопотребление. В случае значительного превышения потребления энергии с высокой долей вероятности в системе находится вирус, который вызывает эту аномалию.


## Диаграмма контекста
![Overview](images/overview.png)

## Базовые сценарии
![get_data](images/base_get_user_data.png)
![programing](images/base_programing_stimul.png)
* Стимуляция сердца

## Основные блоки
![main_modules](images/main_modules.png)
![descriprion](images/descr_main_modules.png)

## Архитектура
![arch](images/arch_hla.png)

## Базовый сценарий и HLA
![base](images/base_prog_hla.png)

## Негативные сценарии
![1](images/attack_programing_conn.png)
![2](images/attack_prog_con_proccessing.png)
![3](images/attack_csu.png)
![4](images/attack_command_block.png)
![5](images/attack_data_procces.png)
![6](images/attack_database.png)

## Политика архитектуры
### Итерации разработки
Начальный этап разработки

![Modules](images/modules.png)

Разбиение сложного компонента

![step2](images/modules_2.png)

Оптимизация стимуляции

![step3](images/final_arch_hla.png)

Уменьшение доверенной кодовой базы

![step4](images/super_final_arch_hla.png)

Обоснование доверия

![rel](images/level_of_rel.png)

## Тесты
