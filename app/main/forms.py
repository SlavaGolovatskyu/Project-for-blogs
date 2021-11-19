from flask_wtf import FlaskForm
from app.models import Role


from wtforms import (
	StringField,
	SubmitField,
	TextAreaField,
	BooleanField,
	PasswordField,
	FileField,
	SelectField
)

from wtforms.validators import (
	DataRequired, 
	Email, 
	Length
)

from flask_wtf.file import FileAllowed


class AddIpForm(FlaskForm):
	ip = StringField('Ип: ', validators=[DataRequired()],
					  render_kw={"placeholder": "192.168.1.1"})
	submit = SubmitField('Добавить/Удалить Ип')

class BanForm(FlaskForm):
	time = StringField("Время: ", validators=[DataRequired()], 
					   render_kw={"placeholder": "Укажите время. Например: 1d25m30s 1 day 25 mins 30 secs"})
	are_you_sure = BooleanField("Вы уверены что хотите забанить?", validators=[DataRequired()])
	submit = SubmitField('Сохранить изменения')


class EditProfileAdminForm(FlaskForm):
	email = StringField("Email: ", validators=[DataRequired(), Email()])
	username = StringField("Username", validators=[DataRequired(), Length(min=6, max=40, message=None)])
	role = SelectField('Role', coerce=int)
	location = StringField('Location', validators=[Length(0, 64)])
	about_me = TextAreaField('About me')
	submit = SubmitField('Сохранить изменения')

	def __init__(self, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]


class EditProfileForm(FlaskForm):
	image = FileField(u'Image File', validators=[FileAllowed(['jpg', 'png', 'gif', 'jpeg'])])
	username = StringField("Username", validators=[DataRequired(), Length(min=6, max=40, message=None)])
	email = StringField("Email: ", validators=[DataRequired(), Email()])
	city = StringField('City: ', validators=[DataRequired(), Length(min=2, max=40, message=None)])
	about_me = TextAreaField('About me: ', validators=[DataRequired(),
													   Length(min=1, max=500, message=None)],
										   render_kw={"placeholder": "Расскажите о себе"})
	new_pass = StringField('New password: ', render_kw={"placeholder": "Введите новый пароль."})
	submit = SubmitField("Сохранить изменения")


class SearchNeedPeopleForm(FlaskForm):
	username = StringField("Username",
						   render_kw={"placeholder": "username"})
	email = StringField("Email: ", render_kw={"placeholder": "email"})
	submit = SubmitField("Искать")


class RegistrationForm(FlaskForm):
	username = StringField("Username", validators=[DataRequired(), Length(min=6, max=40, message=None)],
						    render_kw={"placeholder": "username"})
	email = StringField("Email: ", validators=[Email(), DataRequired()], render_kw={"placeholder": "email"})
	password = PasswordField("Password: ", validators=[DataRequired(), Length(min=6, max=50, message=None)],
							 render_kw={"placeholder": "password"})
	remember = BooleanField("Remember Me")
	submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()], render_kw={"placeholder": "email"})
	password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=50, message=None)],
							 render_kw={"placeholder": "password"})
	remember = BooleanField("Remember Me")
	submit = SubmitField("Войти")


"""
	Custom validators
We will step through the evolution of writing a length-checking validator similar to the built-in Length validator, starting from a case-specific one to a generic reusable validator.

Let’s start with a simple form with a name field and its validation:

class MyForm(Form):
	name = TextField('Name', [Required()])

	def validate_name(form, field):
		if len(field.data) > 50:
			raise ValidationError('Name must be less than 50 characters')
Above, we show the use of an in-line validator to do validation of a single field. In-line validators are good for validating special cases, but are not easily reusable. If, in the example above, the name field were to be split into two fields for first name and surname, you would have to duplicate your work to check two lengths.

So let’s start on the process of splitting the validator out for re-use:

def my_length_check(form, field):
	if len(field.data) > 50:
		raise ValidationError('Field must be less than 50 characters')

class MyForm(Form):
	name = TextField('Name', [Required(), my_length_check])
All we’ve done here is move the exact same code out of the class and as a function. Since a validator can be any callable which accepts the two positional arguments form and field, this is perfectly fine, but the validator is very special-cased.

Instead, we can turn our validator into a more powerful one by making it a factory which returns a callable:

def length(min=-1, max=-1):
	message = 'Must be between %d and %d characters long.' % (min, max)

	def _length(form, field):
		l = field.data and len(field.data) or 0
		if l < min or max != -1 and l > max:
			raise ValidationError(message)

	return _length

class MyForm(Form):
	name = TextField('Name', [Required(), length(max=50)])
Now we have a configurable length-checking validator that handles both minimum and maximum lengths. When length(max=50) is passed in your validators list, it returns the enclosed _length function as a closure, which is used in the field’s validation chain.

This is now an acceptable validator, but we recommend that for reusability, you use the pattern of allowing the error message to be customized via passing a message= parameter:

class Length(object):
	def __init__(self, min=-1, max=-1, message=None):
		self.min = min
		self.max = max
		if not message:
			message = u'Field must be between %i and %i characters long.' % (min, max)
		self.message = message

	def __call__(self, form, field):
		l = field.data and len(field.data) or 0
		if l < self.min or self.max != -1 and l > self.max:
			raise ValidationError(self.message)

length = Length
"""


"""  
	WTForms
	WTForms – это мощная библиотека, написанная на Python и независимая от фреймворков. Она умеет генерировать формы,
	проверять их и предварительно заполнять информацией (удобно для редактирования) и многое другое. 
	Также она предлагает защиту от CSRF. Для установки WTForms используется Flask-WTF.
	Flask- WTF – это расширение для Flask, которое интегрирует WTForms во Flask. Оно также предлагает дополнительные функции,
	такие как загрузка файлов, reCAPTCHA, интернационализация (i18n) и другие. Для установки Flask-WTF нужно ввести следующую команду pip install flask-wtf
	
	
	Пакет wtform предлагает несколько классов, представляющих собой следующие поля:
	StringField, PasswordField, SelectField, TextAreaField, SubmitField
	
	
	использовать несколько валидаторов, разделив их запятыми (,). Модуль wtforms.validators предлагает базовые валидаторы,
	но их можно создавать самостоятельно. В этой форме используются два встроенных валидатора: DataRequired и Email.
	DataRequired: он проверяет, ввел ли пользователь хоть какую-информацию в поле.
	Email: проверяет, является ли введенный электронный адрес действующим.
	Введенные данные не будут приняты до тех пор, пока валидатор не подтвердит соответствие данных.

	Learn Flask#2>python app.py shell
	>>> from forms import ContactForm
	>>> from werkzeug.datastructures import MultiDict
	>>> form1 = ContactForm(MultiDict([('name', 'jerry'),('email', 'jerry@mail.com')]))
	>>> form1.validate()
	False
	>>> form1.error
	Traceback (most recent call last):
	  File "<console>", line 1, in <module>
	AttributeError: 'ContactForm' object has no attribute 'error'
	>>> form1.errors
	{'message': ['This field is required.'], 'csrf_token': ['The CSRF token is missing.']}


	Стоит обратить внимание, что данные передаются в виде объекта MultiDict, потому что функция-конструктор класса wtforms.Form принимает аргумент типа MutiDict. Если данные формы не определены при создании экземпляра объекта формы, а форма отправлена с помощью запроса POST, wtforms.Form использует данные из атрибута request.form. Стоит вспомнить, что request.form возвращает объект типа ImmutableMultiDict. Это то же самое, что и MultiDict, но он неизменяемый.

	Метод validate() проверяет форму. Если проверка прошла успешно, он возвращает True, если нет — False.

	>>>
	>>> form1.validate()
	False
	>>>
	Форма не прошла проверку, потому что обязательному полю message при создании объекта формы 
	не было передано никаких данных. Получить доступ к ошибкам форм можно с помощью атрибута 
	errors объекта формы:

	>>>
	>>> form1.errors
	{'message': ['This field is required.'], 'csrf_token': ['The CSRF token is missing.']}
	>>>
	Нужно обратить внимание, что в дополнение к сообщению об ошибке для поля message, вывод также 
	содержит сообщение об ошибке о недостающем csfr-токене. Это из-за того что в данных формы нет 
	запроса POST с csfr-токеном.

	Отключить CSFR-защиту можно, передав csfr_enabled=False при создании экземпляра класса формы. Пример:
	
	>>> form3 = ContactForm(MultiDict([('name', 'spike'),('email', 'spike@mail.com')]), csrf_enabled=False)
	>>>
	>>> form3.validate()
	False
	>>>
	>>> form3.errors
	{'message': ['This field is required.']}
"""
