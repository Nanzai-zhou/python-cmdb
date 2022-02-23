from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from datetime import datetime
from .models import  User
import json
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
    # index页面会在一个列表中展示所有用户的信息，所以需要获得一组用户的实例
    print(request.session.get('user'))
    users = User.get_list()
    # 但是User实例并不能直接传给模版，需要将用户实例转换成字典
    userdata = []
    for user in users:
        userdata.append(user.to_dict())
    return render(request, 'user/index.html', {'current_time': datetime.today().isoformat(' '), 'users': userdata})

def login(request):
    # 当请求方式为GET时，展示用户登录页面
    if request.method == 'GET':
        return render(request, 'user/login.html')
    # 当请求方式为POST时，需要验证用户名和密码是否正确
    # 当验证失败时，返回错误信息，当验证成功后，重定向到index页面
    if request.method == 'POST':
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = User.valid_login(username, password)
        if user is None:
            return render(request, 'user/login.html', {"error": "用户名或密码错误！"})
        else:
            userdata = user.to_dict()
            request.session['user'] = userdata
            return redirect('user:index')

def logout(request):
    request.session.flush()
    return redirect('user:login')

@check_session
def delete(request):
    id = request.GET.get('id', None)
    user = User.get_user_by_id(id)
    if user:
        user.delete()
    return redirect('user:index')

@check_session
def edit(request):
    id = request.GET.get('id', None)
    user = User.get_user_by_id(id)
    if not user:
        return redirect('user:index')
    userdata = user.to_dict()
    return render(request, 'user/edit.html', {"user": userdata})

@check_session
def change(request):
    id = request.POST.get('id', '')
    print(f'func[change]: id={id}')
    name = request.POST.get('name', '')
    age = request.POST.get('age', '')
    sex = request.POST.get('sex', '')
    tel = request.POST.get('tel', '')
    User.change(id, name, age, sex, tel)
    return redirect('user:index')

@check_session
def signup(request):
    return render(request, 'user/signup.html')

@check_session
def create(request):
    name = request.POST.get('name', None)
    password = request.POST.get('password', None)
    age = request.POST.get('age', '')
    sex = request.POST.get('sex', '')
    tel = request.POST.get('tel', '')
    result = User.signup(name,password,age,sex,tel)
    if result['result'] != 0:
        return render(request, 'user/signup.html', {"error": result['reason']})

    else:
        return redirect('user:index')

@check_session
def create_ajax(request):
    result = User.signup_ajax(request.POST)
    print(f"func=>[views.create_ajax] result={result} type={type(result)}")
    return JsonResponse(result)

@check_session
def delete_ajax(request):
    id = request.GET.get('id', None)
    user = User.get_user_by_id(id)
    user.delete()
    return JsonResponse({"code": 200, "result": "用户删除成功"})

@check_session
def edit_ajax(request):
    id = request.POST.get('id', None)
    name = request.POST.get('name', '')
    age = request.POST.get('age', '')
    sex = request.POST.get('sex', '')
    tel = request.POST.get('tel', '')
    User.change(id, name, age, sex, tel)
    return JsonResponse({"code": 200, "result": "用户修改成功"})



