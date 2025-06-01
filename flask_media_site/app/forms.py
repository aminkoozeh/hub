from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, BooleanField, SelectField, FileField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from flask_wtf.file import FileAllowed, FileRequired
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired()])
    password = PasswordField('رمز عبور', validators=[DataRequired()])
    submit = SubmitField('ورود')

class RegisterForm(FlaskForm):
    username = StringField('نام کاربری', validators=[DataRequired(), Length(min=3, max=25)])
    password = PasswordField('رمز عبور', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('تکرار رمز عبور', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('ثبت نام')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('نام کاربری قبلاً ثبت شده است.')

class UploadForm(FlaskForm):
    title = StringField('عنوان فایل', validators=[DataRequired()])
    description = TextAreaField('توضیحات')
    file_type = SelectField('نوع فایل', choices=[('book', 'کتاب'), ('audio', 'صوتی'), ('video', 'ویدئویی')], validators=[DataRequired()])
    category = SelectField('دسته بندی', coerce=int)
    file = FileField('فایل', validators=[FileRequired(), FileAllowed(['pdf', 'mp3', 'mp4', 'wav', 'm4a', 'txt', 'epub', 'mobi'], 'فقط فرمت‌های مجاز!')])
    poster = FileField('پوستر (تصویر)', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'فقط تصاویر!')])
    is_special = BooleanField('فایل ویژه')
    submit = SubmitField('آپلود')

class CategoryForm(FlaskForm):
    name = StringField('نام دسته بندی', validators=[DataRequired()])
    submit = SubmitField('ثبت دسته بندی')
