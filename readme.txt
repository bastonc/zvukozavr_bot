Алгоритм работы
После присоединения бота к чату
необходимо выполнить команду /addAdmin - если команда вполняется первый раз - то пользователь выполнивший ее -
автоматически становится ROOT пользователем. Все дальнейшие попытки выполнить эту команду другими людьми - будут
добавлятся в предложку админов. ROOT пользователь или любой из уже одобренных администраторов, могут посмотерть предложку
админа командой /rootAdmins в этом меню есть возможность одобрить или удалить пользователя на роль администратора бота.
Бот способен работать в двух режимах:  Prod - когда бот работает в живом чате. В этом режиме блокируются такие команды
как /clearAdmin, а так же блокируется вывод отладочной информации в консоль (в случае запуска из консоли);
Devel - режим отладки и разработки. В нем можно удалить всех администраторов, а так же видеть служебный вывод.
Для работы на живом чате - установить mode=Prod

-------------------------------------------------------------------
 Список команд
/pozorToday - список тех кто сегодня присылал войсы (выполняется в чате)
/pozorAll - список общий, всех кто присылал войсы вообще в чат (все кто есть в базе) (выполняется в чате)
/addMessage - позволяет предлагать сови ругательные сообщения.
              Все поступившие сообщения отпарвляются на модерацию
              Формат /add Текст сообщения (выполняется в чате)
/clearAll - команда удаляет всех пользователей. Команда работает только от юзера ID котрого занесено
            в базу Админов (выполянется в ЛС бота). Работет с данными чата, ID которого привязан к конкретному
            пользователю - как администратору чата)
/adminMessage - вход в режим модерации сообщений. оступно только для пользователей чей ID и группа
                находятся в базе Админов (выполянется в ЛС бота)
/adminMessageAll - отображает все сообщения в базе с возожностью удалить (выполянется в ЛС бота)
/addAdmin - команда которая предлагает текущего пользователя в админы. Если База админов пуста - тогда
            текущий  пользователь автоматически становится главным админом(ROOT). В противном случае кандидатура
            должна будет пройти модерацию ROOTом
/сlearAdmin - команда которая удаляет всех админов, обнуляя в т.ч главного (первого) Админа (выполянется в ЛС бота,
                только в режиме Develop)
/allAdmins - команда показывает всех Админов бота (выполянется в ЛС бота)

---------
/clearAdmin - удалить всех админов. Отладочная