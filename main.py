from flask import render_template, request, redirect, session, url_for, jsonify ,send_from_directory,make_response
from config import *
from model import *
import json, uuid, os, copy
from flask_mail import Message, Mail
from flask_uploads import UploadSet, configure_uploads


# 发送邮件初始化
mail = Mail()
mail.init_app(app)
# 上传文件初始化
app.config['UPLOAD_PATH'] = 'upload'
app.config['UPLOADS_DEFAULT_DEST'] = app.config['UPLOAD_PATH']
app.config['UPLOADS_DEFAULT_URL'] = 'http://127.0.0.1:5000/'
uploaded_file = UploadSet()
configure_uploads(app, uploaded_file)

## 登录 #
# 登陆页面
# 需要完成：异常处理，对返回值的处理
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        usern = request.form.get('Username')
        passw = request.form.get('Password')
        user = User.query.filter_by(User_name = usern).first()
        if user:
            U_Type =''
            if user.Type_admin == 1:
                U_Type = U_Type + '管理员 '
            if user.Type_Course_teacher == 1:
                U_Type = U_Type + '授课教师 '
            if user.Type_Course_leader == 1:
                U_Type = U_Type + '授课教师 '
            if user.Type_Major_leader == 1:
                U_Type = U_Type + '授课教师 '  
            print(U_Type)         
            session['user_name'] = usern
            session['user_type'] = U_Type
            session.permanent = True
            if user.User_password == passw:
                return redirect(url_for('index'))
            else:
                return u' password error'
        else:
            return u' username  not existed'


## 注册 #
# 发送邮箱验证码
# 需要完成：异常处理，返回值的处理
@app.route('/email_captcha')
def email_captcha():
    email = request.args['email']
    if email:
        captcha = str(uuid.uuid1())[:6]
        message = Message('西安邮电大学，专业认证信息管理系统', recipients=[
                          email], body='您的验证码是：%s' % captcha)
        mail.send(message)
    cache.set('email', captcha)
    return {}

# 提交注册表，并返回信息
# 需要完成：对异常的处理,教工号已经存在的情况
@app.route('/register_post', methods=['GET', 'POST'])
def register_post():
    result = request.get_json()
    if(request.method == 'POST'):
        if result["registerVerification_code"] == cache.get('email'):
            _user = User(User_num=result['registerUsernum'], User_name=result["registerUsername"],
                         User_email=result["registerEmail"], User_password=result["registerPassword"], Type_id=2)
            db.session.add(_user)
            db.session.commit()
            return jsonify({"success": 200, "msg": "注册成功"})
        return jsonify({"error": 1001, "msg": "注册失败"})


# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


## 上下文处理器 #
# 需要完成：只完成了任课教师和管理员，需要完成其他类型用户的登录显示 ，返回值的处理
@app.context_processor
def mycontext():
    usern = session.get('user_name')
    usertype = session.get('user_type')
    index_in = 'course_info'
    if usern:
        if usertype == '管理员 ':
            index_in = 'admin_user_center'
        return {'username': usern, 'usertype': usertype, 'index_in': index_in}
    else:
        return {}


# 主页面
# 判断用户的类型，展示不用的左侧导航栏#
# 需要完成：完成其他类型用户
@app.route('/index', methods=['GET', 'POST'])
def index():
    usertype = session.get('user_type')
    if usertype:
        if usertype == '管理员 ':
            left_navigate_vars = [('layui-this', 'admin_user_center', 'layui-icon-group', '用户中心'), ('','upload_courses_table', 'layui-icon-file', '上传课表'), ('', 'admin_course_table', 'layui-icon-list', '查看课表')]
        if usertype == '授课教师 ':
            left_navigate_vars = [('layui-this', 'course_info', 'layui-icon-home',
                                   '课程信息'), ('', 'personal', 'layui-icon-about', '个人中心')]
        if usertype == 3:
            pass  # 课程负责人
        if usertype == 4:
            pass  # 专业负责人
    return render_template('index.html', left_navigate_vars=left_navigate_vars)


## 任课教师 #
# 教师，课程信息
# 需要完成：异常处理
@app.route('/caurse_info_data')
def caurse_info_data():
    usern = session.get('user_name')
    courses = Course.query.filter_by(Course_teacher = usern).all()
    page = int(request.args["page"])
    limit = int(request.args["limit"])
    payload = []
    for course in courses:
        jcourse = course.to_json()
        payload.append(jcourse)
    rst = {"code": 0, "msg": "", "data": payload}
    rst["count"] = len(rst["data"])
    rst["data"] = rst["data"][(page-1)*10: (page-1)*10 + limit]
    return json.dumps(rst, ensure_ascii=False)

# 上传图片
# 页面停留事件过长，需要刷新
@app.route('/teacher_upload_updata', methods=['GET', 'POST'])
def teacher_upload_updata():
    if request.method == 'GET':
        course_id = request.args.get('course_id')
        Course_major = request.args.get('Course_major')
        Course_class = request.args.get('Course_class')
        Course_teacher = request.args.get('Course_teacher')
        file_path = ''+Course_major+'/'+Course_teacher+'/'+Course_class+''
        cache.set('course_id', course_id)
        cache.set('file_path', file_path)
    if request.method == 'POST':
        file = request.files['file']
        try:
            course_id = cache.get('course_id')
            file_path = cache.get('file_path')
            filename = uploaded_file.save(file, folder=file_path ,name=file.filename)
            result = Course.query.filter_by(id = course_id).first()
            result.Course_state = 2
            result.info = '授课教师已经提交材料\n'
            upf = Up_file(course_id = course_id , Material_upload = filename)
            db.session.add(upf)
            db.session.commit()
            return jsonify({'code': 0})
        except Exception as e:
            return jsonify({'code': -1, 'filename': '', 'msg': 'Error occurred'})
    else:
        return jsonify({'code': -1, 'filename': '', 'msg': 'Method not allowed'})

# 上传文件并预览页面
@app.route('/teacher_upload', methods=['GET', 'POST'])
def teacher_upload():
    course_id = cache.get('course_id')
    result = Up_file.query.filter_by(course_id = course_id).all()
    payload = copy.deepcopy(result)
    for p in payload:
        p.Material_upload = os.path.basename(p.Material_upload)
    return render_template('teacher_upload.html',payload = payload)

@app.route('/up_file_de',methods=['GET', 'POST'])
def up_file_de():
    file_id = request.args.get('file_id')
    if file_id:
        result = Up_file.query.filter_by(id = file_id).first()
        os.remove('E:/Vscode/python/final/upload/files/'+result.Material_upload)
        db.session.delete(result)
        db.session.commit()
        return jsonify({'code': 0, 'msg': 'success'})
    return jsonify({'code': -1, 'msg': 'error'})

@app.route('/up_file_se/<file_id>',methods=['GET', 'POST'])
def up_file_se(file_id):
    if file_id:
        result = Up_file.query.filter_by(id = file_id).first()
        return send_from_directory(directory = app.config['UPLOAD_PATH'],filename=result.Material_upload,as_attachment=True)  
    return 'error'

@app.route('/cancel_up_file',methods=['GET', 'POST'])
def cancel_up_file():
    course_id = request.args.get('course_id')
    if course_id:
        result = Up_file.query.filter_by(course_id = course_id).all()
        if not result:
            _result = Course.query.filter_by(id = course_id).first()
            _result.Course_state = 1
            _result.info = '授课教师还未提交材料\n'
            db.session.commit()
        return jsonify({'code': 0, 'msg': 'success'})
    return jsonify({'code': -1, 'msg': 'error'})

@app.route('/course_info_details/<course_id>', methods=['GET', 'POST'])
def course_info_details(course_id):
    result = Up_file.query.filter_by(course_id = course_id).all()
    _result = Course.query.filter_by(id = course_id).first()
    jresult = _result.to_json()
    upd_file = []
    for res in result:
        upd_file.append( os.path.basename(res.Material_upload))
    upd_file_str = ','.join(upd_file)
    if not upd_file_str:
        upd_file_str = '无'
    return render_template('course_info_details.html',jresult=jresult,upd_file_str=upd_file_str)

# 课程信息页面
@app.route('/course_info', methods=['GET', 'POST'])
def course_info():
    return render_template('course_info.html')

# 任课教师个人中心页面
@app.route('/personal', methods=['GET', 'POST'])
def personal():
    return render_template('personal.html')

## 管理员 #
# 数据库所有用户信息
# 需要完成：异常处理，返回值的处理
@app.route('/admin_user_center_getdata', methods=['GET', 'POST'])
def admin_user_center_getdata():
    if request.method == 'GET':
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        users = User.query.all()
        payload = []
        for user in users:
            juser = user.to_json()
            payload.append(juser)
        rst = {"code": 0, "msg": "", "data": payload}
        rst["count"] = len(rst["data"])
        rst["data"] = rst["data"][(page-1)*10: (page-1)*10 + limit]
        return json.dumps(rst, ensure_ascii=False)
    if request.method == 'POST':
        user_type = Type.query.all()
        payload = []
        for type in user_type:
            jtype = type.to_json()
            payload.append(jtype)
        rst = payload
        return json.dumps(rst, ensure_ascii=False)
    return {}

# 修改用户信息保存到数据库
# 需要完成：异常处理，返回值的处理
@app.route('/admin_user_center_updata', methods=['GET', 'POST'])
def admin_user_center_updata():
    if request.method == 'GET':
        _num = request.args.get('User_num')
        if _num:
            result = User.query.filter_by(User_num = _num).first()
            db.session.delete(result)
            db.session.commit()
        return {}
    if request.method == 'POST':
        data = request.get_json()
        if data:
            result = User.query.filter_by(User_num = data['User_num']).first()
            result.Type_id = data['_Type_id']
            db.session.commit()
        return {}

# 用户中心页面
@app.route('/admin_user_center', methods=['GET', 'POST'])
def admin_user_center():
    return render_template('admin_user_center.html')

# 上传课表到数据库
# 需要完成：异常处理，返回值的处理
# 管理员可以查看所有课程信息，并且可以修改课表数据#
@app.route('/upload_courses_table_updata', methods=['GET', 'POST'])
def upload_courses_table_updata():
    data = request.get_json()
    all_courses = []
    if(request.method == 'POST'):
        if data:
            Course.query.delete()
            for k in data:
                course = Course(Course_name=k['课程名称']
                                ,Course_college=k['学院']
                                ,Course_class=k['班级']
                                ,Course_major=k['专业']
                                ,Course_teacher=k['授课教师']
                                ,Course_leader=k['课程负责人']
                                ,Major_leader=k['专业负责人']
                                ,Course_state=1
                                ,info = '授课教师还未提交材料\n')
                all_courses.append(course)
        db.session.add_all(all_courses)
        db.session.commit()
        return {}

# 上传课表页面
@app.route('/upload_courses_table', methods=['GET', 'POST'])
def upload_courses_table():
    return render_template('upload_courses_table.html')

# 修改课表页面
@app.route('/admin_course_table', methods=['GET', 'POST'])
def admin_course_table():
    return render_template('admin_course_table.html')

@app.route('/admin_course_table_getdata', methods=['GET', 'POST'])
def admin_course_table_getdata():
    courses = Course.query.all()
    page = int(request.args["page"])
    limit = int(request.args["limit"])
    payload = []
    for course in courses:
        jcourse = course.to_json()
        payload.append(jcourse)
    rst = {"code": 0, "msg": "", "data": payload}
    rst["count"] = len(rst["data"])
    rst["data"] = rst["data"][(page-1)*10: (page-1)*10 + limit]
    return json.dumps(rst, ensure_ascii=False)

@app.route('/admin_course_table_updata', methods=['GET', 'POST'])
def admin_course_table_updata():
    if request.method == 'GET':
        _course_id = request.args.get('course_id')
        _operate = request.args.get('operate')
        if _course_id and _operate == 'del':
            result = Course.query.filter_by(id = _course_id).first()
            db.session.delete(result)
            db.session.commit()
        if _course_id and _operate == 'edit':
            cache.set('edit_id', _course_id) #edit_id管理员修改课表页面中，点击修改，传过来的id，先存起来
        return jsonify({'code': 0, 'msg':'删除成功'})
    return jsonify({'code': -1, 'msg':'操作失败'})

@app.route('/admin_alter_course', methods=['GET', 'POST'])
def admin_alter_course():
    _course_id = cache.get('edit_id')
    result = Course.query.filter(Course.id == _course_id).first()
    return render_template('admin_alter_course.html', result = result)

@app.route('/admin_alter_course_updata', methods=['GET', 'POST'])
def admin_alter_course_updata():
    if request.method == 'GET':
        _course_id = cache.get('edit_id')
        result = Course.query.filter_by(id = _course_id).first()
        result.Course_name = request.args["Course_name"]
        result.Course_college = request.args["Course_college"]
        result.Course_major = request.args["Course_major"]
        result.Course_class = request.args["Course_class"]
        result.Course_teacher = request.args["Course_teacher"]
        result.Course_leader = request.args["Course_leader"]
        result.Major_leader = request.args["Major_leader"]
        db.session.commit()
    pass

if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    app.run(debug=True)