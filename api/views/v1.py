from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from asset.models import Host,Resource
import json

class ApiView(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        return super(ApiView, self).dispatch(request, *args, **kwargs)

    def response(self, code=200, result={}, error=''):
        return JsonResponse({'code': code, 'result': result, 'error': error})

class ClientView(ApiView):

    # get请求处理方法，用于获取client的信息，去数据库中找到对应ip的client记录，然后组装成字典，使用JsonResponse返回
    def get(self, request, *args, **kwargs):
        _clientInfo = {}
        ip = kwargs.get('ip', '')
        try:
            _client = Host.objects.get(ip=ip)
        except models.ObjectDoesNotExist as e:
            return self.response(result=_clientInfo, error='client not exist')
        _clientInfo = _client.as_dict()
        return self.response(result=_clientInfo)

    # post请求处理方法，用于创建或修改一条client记录
    def post(self, request, *args, **kwargs):
        ip = kwargs.get('ip', '')
        param = json.loads(request.body)
        _instance = Host.register_or_replace(ip, **param)
        _clientInfo = _instance.as_dict()
        return self.response(result=_clientInfo)

    # put请求处理方法，用于更新一条client记录
    def put(self, request, *args, **kwargs):
        ip = kwargs.get('ip', '')
        param = json.loads(request.body)
        try:
            _client = Host.objects.get(ip=ip)
            _instance = Host.register_or_replace(ip, **param)
            _clientInfo = _instance.as_dict()
            return self.response(result=_clientInfo)
        except models.ObjectDoesNotExist as e:
            return self.response(error='client not exist')

    # delete请求处理方法，用于删除一条client记录
    def delete(self, request, *args, **kwargs):
        ip = kwargs.get('ip', '')
        try:
            _client = Host.objects.get(ip=ip)
            _client.delete()
            return self.response(error='client delete success')
        except models.ObjectDoesNotExist as e:
            return self.response(error='client not exist')

class ResourceView(ApiView):

    # post请求处理方法，用于创建一条资源利用率记录。
    def post(self, request, *args, **kwargs):
        ip = kwargs.get('ip', '')
        param = json.loads(request.body)
        _res = Resource.create(ip, **param)
        return self.response(error="resource created")

class HeartBeatView(ApiView):

    # post请求处理方法，用于修改heartbeat时间
    def post(self, request, *args, **kwargs):
        ip = kwargs.get('ip', '')
        Host.heartbeat(ip)
        return self.response(error="heartbeat time update")