I am creating my first web application in which you can publish your articles,
update / delete your articles, but for publishing your articles you must sign-up, 
there is also an admin panel. Helps me with this: Flask, SQLAlchemy, WTForms,
to begin with took the SQlite3 database, also Alembic for database migration.
A little HTML, CSS and Bootstrap. Also JavaScript for chat.

you can see my project in this video: https://www.youtube.com/watch?v=zDitd__Hsxo (old version)
https://www.youtube.com/watch?v=rGOFdRBtvjY (new version)

also you can see my project on http://slavik141.pythonanywhere.com/

UPD (10.06.21)
After the announcement of the end of work on the project. It occurred to me to add to it a chat built on sockets. 
Now the main targets are: add mut(-) now that's not important, ban(+) ban was added, update the chat itself(+) chat deleted from web version pythonanywhere can't supports sockets, as well as logs(+)

18.06.21
The sqlite3 database was removed from the project because it cannot reset a column from the table.
From this day on, I will only use PostgreSQL, maybe sometimes MySQL

## Stack:
* Frontend: HTML, CSS, JS, JQuery.
* Backend: Python/Flask, Sockets.

## If you want starting my project you must do:
* Instaling Python
* git clone https://github.com/SlavaGolovatskyu/Project-for-blogs.git
* cd Project-for-blogs
* pip install -r requirements.txt
* python manager.py shell
* db.create_all()
* exit()
* python manager.py runserver
