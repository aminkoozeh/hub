from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import User, File, Category
from app.forms import LoginForm, RegisterForm, UploadForm, CategoryForm

main = Blueprint('main', __name__)

@main.route('/')
def index():
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@main.route('/file/<int:file_id>')
def view_file(file_id):
    file = File.query.get_or_404(file_id)
    # بررسی دسترسی به فایل ویژه
    if file.is_special and (not current_user.is_authenticated or not (current_user.is_special or current_user.is_admin)):
        flash('این فایل فقط برای کاربران ویژه است.')
        return redirect(url_for('main.index'))
    return render_template('view_file.html', file=file)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.admin_dashboard' if current_user.is_admin else 'main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('ورود موفقیت‌آمیز بود.')
            return redirect(url_for('main.index'))
        flash('نام کاربری یا رمز عبور اشتباه است.')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('خروج با موفقیت انجام شد.')
    return redirect(url_for('main.index'))

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('ثبت‌نام با موفقیت انجام شد. اکنون وارد شوید.')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

# پنل ادمین

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('دسترسی غیرمجاز.')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/admin')
@admin_required
def admin_dashboard():
    files = File.query.all()
    return render_template('admin/dashboard.html', files=files)

@main.route('/admin/upload', methods=['GET', 'POST'])
@admin_required
def upload_file():
    form = UploadForm()
    # تنظیم choices دسته بندی برای فرم
    categories = Category.query.all()
    form.category.choices = [(0, 'بدون دسته بندی')] + [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        file_data = form.file.data
        filename = secure_filename(file_data.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file_data.save(file_path)

        poster_filename = None
        if form.poster.data:
            poster_file = form.poster.data
            poster_filename = secure_filename(poster_file.filename)
            poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], poster_filename)
            poster_file.save(poster_path)

        new_file = File(
            title=form.title.data,
            description=form.description.data,
            file_type=form.file_type.data,
            category_id=form.category.data if form.category.data != 0 else None,
            filename=filename,
            poster=poster_filename,
            is_special=form.is_special.data
        )
        db.session.add(new_file)
        db.session.commit()
        flash('فایل با موفقیت آپلود شد.')
        return redirect(url_for('main.admin_dashboard'))

    return render_template('admin/upload.html', form=form)

@main.route('/admin/categories', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    form = CategoryForm()
    categories = Category.query.all()

    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash('این دسته بندی قبلاً وجود دارد.')
        else:
            new_cat = Category(name=form.name.data)
            db.session.add(new_cat)
            db.session.commit()
            flash('دسته بندی جدید اضافه شد.')
        return redirect(url_for('main.manage_categories'))

    return render_template('admin/manage_categories.html', form=form, categories=categories)

@main.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@main.route('/admin/users/promote/<int:user_id>')
@admin_required
def promote_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    db.session.commit()
    flash(f'کاربر {user.username} به ادمین ارتقا یافت.')
    return redirect(url_for('main.manage_users'))

@main.route('/admin/users/special/<int:user_id>')
@admin_required
def toggle_special_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_special = not user.is_special
    db.session.commit()
    status = 'ویژه' if user.is_special else 'عادی'
    flash(f'کاربر {user.username} اکنون {status} است.')
    return redirect(url_for('main.manage_users'))

@main.route('/admin/files/delete/<int:file_id>')
@admin_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    try:
        # حذف فایل و پوستر از سیستم فایل
        if file.filename:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename))
        if file.poster:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], file.poster))
    except Exception as e:
        print(f'خطا در حذف فایل: {e}')
    db.session.delete(file)
    db.session.commit()
    flash('فایل حذف شد.')
    return redirect(url_for('main.admin_dashboard'))

@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@main.route('/search')
def search():
    query = request.args.get('q', '')
    files = []
    if query:
        files = File.query.filter(File.title.ilike(f'%{query}%')).all()
    return render_template('index.html', categories=Category.query.all(), search_query=query, search_results=files)

@main.route('/admin/categories/delete/<int:category_id>')
@admin_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)

    # اگر دسته‌بندی فایل دارد، مانع حذف شو
    if category.files:
        flash('امکان حذف این دسته‌بندی وجود ندارد چون شامل فایل است.')
        return redirect(url_for('main.manage_categories'))

    db.session.delete(category)
    db.session.commit()
    flash('دسته‌بندی حذف شد.')
    return redirect(url_for('main.manage_categories'))
@main.route('/admin/users/demote/<int:user_id>')
@admin_required
def demote_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('نمی‌توانید دسترسی ادمین خودتان را حذف کنید.')
        return redirect(url_for('main.manage_users'))
    user.is_admin = False
    db.session.commit()
    flash(f'دسترسی ادمین از کاربر {user.username} گرفته شد.')
    return redirect(url_for('main.manage_users'))