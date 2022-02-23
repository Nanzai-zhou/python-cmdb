from django.db import models
from hashlib import md5

class User(models.Model):
    name = models.CharField(max_length=32, unique=True, null=False, default='', db_index=True)
    password = models.CharField(max_length=32, null=False, default='')
    age = models.IntegerField(null=False, default=1)
    sex = models.BooleanField(null=False, default=True)
    tel = models.CharField(max_length=20, null=False, default='')
    create_time = models.DateTimeField(null=False,auto_now_add=True)

    @classmethod
    def encrypt_password(cls, password):
        b_password = password.encode()
        md5_tool = md5()
        md5_tool.update(b_password)
        md5_password = md5_tool.hexdigest()
        return md5_password

    def to_dict(self):
        user = dict(id=self.id, name=self.name, age=self.age, sex=self.sex, tel=self.tel, \
                    create_time=self.create_time.strftime('%Y-%m-%d %H:%M:%S'))
        return user

    @classmethod
    def get_list(cls):
        users = User.objects.all()
        return users

    @classmethod
    def valid_login(cls, username, password):
        md5_password = User.encrypt_password(password)
        try:
            user = User.objects.get(name__exact=username, password__exact=md5_password)
            return user
        except Exception as e:
            return None

    @classmethod
    def get_user_by_id(cls, id):
        try:
            user = User.objects.get(id=id)
            return user
        except Exception as e:
            return None

    @classmethod
    def change(cls,id,name,age,sex,tel):
        user = cls.get_user_by_id(id)
        user.name = name
        user.age = age
        user.sex = sex
        user.tel =tel
        user.save()

    @classmethod
    def signup(cls,name,password,age,sex,tel):
        if not name:
            return {"result": 1, "reason": "用户名为空"}
        if not password:
            return {"result": 2, "reason": "密码为空"}
        if User.objects.filter(name=name):
            return {"result": 3, "reason": "用户已存在"}
        md5_password = User.encrypt_password(password)
        user = User(name=name, password=md5_password, age=age, sex=sex, tel=tel)
        user.save()
        return {"result": 0, "reason": "创建成功"}

    @classmethod
    def signup_ajax(cls, request):
        name = request.get('name', None)
        print(f"func=>[models.signup_ajax] name={name}")
        password = request.get('password', None)
        age = request.get('age', '')
        sex = request.get('sex', '')
        tel = request.get('tel', '')
        if not name:
            return {"code": 403, "result": "用户名为空"}
        if not password:
            return {"code": 403, "result": "密码为空"}
        if User.objects.filter(name=name):
            return {"code": 403, "result": "用户已存在"}
        md5_password = User.encrypt_password(password)
        user = User(name=name, password=md5_password, age=age, sex=sex, tel=tel)
        user.save()
        return {"code": 200, "result": "创建成功"}

