from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from .models import Host, Resource
from django.utils import timezone
from datetime import timedelta
from functools import wraps

# Create your views here.

def check_session(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user', None):
            if request.is_ajax():
                return JsonResponse({"code": 400, "result": "用户未登录"})
            return redirect('user:login')
        return func(request)
    return wrapper

@check_session
def index(request):
    return render(request, 'asset/index.html')

def list_ajax(request):
    if not request.session.get('user', None):
        return JsonResponse({"code": 400, "result": []})
    hosts = Host.objects.all()
    result = [ host.as_dict() for host in hosts ]
    print(result)
    return JsonResponse({"code": 200, "result": result})

@check_session
def delete_ajax(request):
    id = request.GET.get('id', None)
    try:
        host = Host.objects.get(id=id)
    except:
        return JsonResponse({"code": 403, "result": "用户不存在"})
    host.delete()
    return JsonResponse({"code": 200, "result": "用户删除成功"})

@check_session
def get_ajax(request):
    id = request.GET.get("id", None)
    try:
        host = Host.objects.get(id=id)
    except:
        return JsonResponse({"code": 403, "result": "用户不存在"})
    result = host.as_dict()
    return JsonResponse({"code": 200, "result": result})

@check_session
def edit_ajax(request):
    id = request.POST.get('id', '')
    try:
        host = Host.objects.get(id=id)
    except:
        return JsonResponse({"code": 403, "result": "资产不存在"})
    ip = request.POST.get('ip', '')
    hostname = request.POST.get('hostname', '')
    platform = request.POST.get('platform','')
    arch = request.POST.get('arch', '')
    mem = request.POST.get('mem', '')
    cpu = request.POST.get('cpu', '')
    host.ip = ip
    host.hostname = hostname
    host.platform = platform
    host.arch = arch
    host.mem = mem
    host.cpu = cpu
    host.save()
    return JsonResponse({'code': 200, 'result': '资产修改成功'})

@check_session
def get_resource_ajax(request):
    id = request.GET.get('id', '')
    try:
        host = Host.objects.get(id=id)
        ip = host.ip
    except:
        return JsonResponse({'code': 403, 'result': '资产不存在'})
    now = timezone.now()
    start_time = now - timedelta(hours=5)
    resources = Resource.objects.filter(ip=ip,time__gte=start_time).order_by('time')
    tem_res = {}
    for res in resources:
        tem_res[res.time.strftime('%Y-%m-%d %H:%M')] = {"cpu": res.cpu_usage, "mem": res.mem_usage}
    xAxis = []
    cpu = []
    mem = []
    while start_time < now:
        str_time = start_time.strftime('%Y-%m-%d %H:%M')
        xAxis.append(str_time)
        cpu.append(tem_res.get(str_time, {}).get("cpu", 0))
        mem.append(tem_res.get(str_time, {}).get("mem", 0))
        start_time = start_time + timedelta(minutes=1)
    return JsonResponse({'code': 200, 'result': [xAxis, cpu, mem]})


