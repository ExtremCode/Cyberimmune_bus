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
Построение безопасной архитектуры и прототипа системы управления электрокардиостимулятором (ЭКС) с интерфейсом удалённого доступа.

Для упрощения разработки было приянто решение разарботать архитектуру ЭКС, имеющего код AAI. Это означает, что:
* Стимулируемая камера - предсердие (A)
* Детектируемая камера - предсердие (A)
* Ингибирование стимулятора в ответ на детектированный сигнал (I)

В дополнение к этому, ЭКС имеет только электроды и повторители, осуществляющие стимуляцию и собирающие обратный импульс соответственно. Отсутствуют какие-либо оптические датчики и акселерометры для сбора всевозможной дополнительной информации о состоянии пациента.

Стоит отметить, что разрабатываемый ЭКС применяется только при диагнозах брадикардии и, возможно, аритмии. Командой разработки это рассматривается как поддержание нормальной частоты сердечных сокращений, и при превышении этого порога стимуляция осуществляется в меньшей степени.

Удаленный интерфейс доступа к ЭКС основан на коммерческой технологии Home Monitoring BIOTRONIK,
суть которой заключается в установлении телеметрической связи между ЭКС и прибором пациента “Cardiomessenger” (на базе модифицированного мобильного телефона) для создания единой замкнутой коммуникационной системы «устройство – “Cardiomessenger” – сервисный центр BIOTRONIK – лечащий врач – пациент».
Устройство пользовательского интерфейса способно принимать данные с ЭКС и передавать их в мед. учреждение, также мы добавили возможность вызова неотложной помощи в случае ухудшения состояния пациента.

## Определение ценностей продукта и негативных сценариев
| Ценность | Негативные события | Величина ущерба | Комментарий |
|:----------:|:----------:|:----------:|:----------:|
| Пациент | Причинение тяжкого вреда здоровью или летальный исход | Высокий | Судебные иски |
| Информация с ЭКС | Компрометация или несанкционированный доступ | Высокий | Нарушение данных приведет к неправильной оценке состояния пациента |
| ЭКС | Выход из строя | Средний | Потребуется обращение в медицинскую организацию в срочном порядке |

## Роли и пользователи
| Роль | Описание |
|:----------:|:----------:|
| Пациент | Использование ЭКС |
| Кардиолог | Настройка ЭКС |

## Цели и предположения безопасности
### Цели безопасности
1. Выполняются команды только от аутентичных и авторизованных пользователей.
2. Команды, которые отвечают за стимуляцию сердца, не причиняют вред здоровью пациента. (Пока принято решение об исключении этой ццели безопасности ввиду того, что она достигается путем выполнения команд только от аутентичных и авторизованных пользователей, являющихся благонадежными. Также команды подбираются индивидуально для каждого пациента, следовательно, проверить их на опасность достаточно сложно. Можно только выделить очевидно опасные команды, посылающие очень высокий импульс, но для их отсеивания нет необходимости создавать отдельный модуль или писать много кода.)
3. Доступ к конфиденциальной информации ЭКС имеют только аутентичные и авторизованные пользователи.
4. Временные показатели частоты сердечного ритма и другая информация о состоянии пациента, хранящаяся в библиотеке данных, достоверны и не противоречивы.

### Предположения безопасности
1. Данные, получаемые с датчиков ЭКС, достоверны. (Стоит отметить, что хоть и данные с датчиков достоверны, но они могут исказиться см. "Дополнительные меры защиты". Учитывая, что датчики содержатся в устройстве, программную архитектуру которого мы разрабатываем, мы несем некоторую ответственность за них. Этим предположением мы гарантируем себе то, что датчики физически работают корректно.)
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
![2](images/attack_prog_con_poccessing.png)
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

Была пересмотрена постановка задачи и немного упрощена и уточнена. Исключены коммутаторы ввиду того, что они теоретически не содержат программного кода и являются физическими устройствами. Упразднена ЦБ 2, поэтому блок управления командами стал проще. Было оптимизировано максимальное число всех интерфейсов для одного блока среди всех блоков, теперь оно 6 вместо 8. Вместо ЦСУ стал Концентратор информации системы, который отвечает за сбор информации с блоков, передачу команд для стимуляции, а также отправку ошибок и всей информации для последующей пересылки обработчику входящих запросов.

![step5](images/another_arch_hla.png)

Обоснование доверия выглядит следующим образом

![rel2](images/lev_of_rel2.png)

## Тесты
