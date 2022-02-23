from django.db import models
from datetime import datetime, timezone, timedelta

# Create your models here.

class BaseAttrDictMixin(object):
    # as_dict将对象属性中常用的基本数据类型及内置数据结构转换成字典，为json序列化做准备
    def as_dict(self):
        _dict = {}
        for _key, _value in self.items():
            if isinstance(_key, (int, str, float, datetime, bytes, bool, tuple, list, )):
                _dict[_key] = _value
        return _dict

class Host(BaseAttrDictMixin, models.Model):
    hostname = models.CharField(max_length=64, null=False, default='')
    ip = models.GenericIPAddressField(default='0.0.0.0', unique=True, db_index=True)
    mac = models.CharField(max_length=64, default='')
    platform = models.CharField(max_length=128, default='')
    arch = models.CharField(max_length=16, default='')
    cpu = models.IntegerField(default=0)
    mem = models.BigIntegerField(default=0)
    pid = models.IntegerField(default=0)
    user = models.CharField(max_length=256, default='')
    application = models.CharField(max_length=256, default='')
    position = models.CharField(max_length=256, default='')
    remark = models.CharField(max_length=512, default='')
    heartbeat_time = models.DateTimeField(auto_now_add=True)
    register_time = models.DateTimeField(auto_now_add=True)
    modify_time = models.DateTimeField(auto_now=True)

    @property
    def is_online(self):
        return datetime.now() - self.heartbeat_time < timedelta(minutes=5)

    @classmethod
    def register_or_replace(cls, ip, **kwargs):
        _instance = None
        try:
            _instance = cls.objects.get(ip=ip)
        except models.ObjectDoesNotExist as e:
            _instance = cls()
            setattr(_instance, 'ip', ip)
        for _key, _value in kwargs.items():
            if hasattr(_instance, _key):
                setattr(_instance, _key, _value)
        _instance.save()
        return _instance

    @classmethod
    def heartbeat(cls, ip):
        try:
            _instance = cls.objects.get(ip=ip)
            _instance.heartbeat_time = datetime.now()
            _instance.save()
        except models.ObjectDoesNotExist as e:
            pass

    def as_dict(self):
        _dict = {}
        for k, v in self.__dict__.items():
            if isinstance(v, (int, str, float, datetime,)):
                _dict[k] = v
        return _dict

class Resource(BaseAttrDictMixin, models.Model):
    ip = models.GenericIPAddressField(default='0.0.0.0', db_index=True)
    cpu_usage = models.FloatField(default=0)
    mem_usage = models.FloatField(default=0)
    time = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, ip, **kwargs):
        _instance = cls()
        setattr(_instance, 'ip', ip)
        for _key, _value in kwargs.items():
            if hasattr(_instance, _key):
                setattr(_instance, _key, _value)
        _instance.save()
        return _instance