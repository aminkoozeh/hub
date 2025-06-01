from app import create_app, db
from app.models import Category, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # ایجاد دسته‌بندی‌ها
    categories = ['کتاب', 'موسیقی', 'ویدئو']
    for name in categories:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

    # ساخت کاربر ادمین پیش‌فرض
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', is_admin=True)
        admin_user.set_password('admin123')
        db.session.add(admin_user)

    db.session.commit()
    print("داده‌های اولیه با موفقیت اضافه شدند.")
