from flask import Flask
from flask_caching import Cache


cache = Cache()

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@127.0.0.1/professional_certification' # 配置数据库

app.config['SECRET_KEY'] = 'hard to guess'

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# 邮箱配置
# MAIL_USE_TLS：端口号587
# MAIL_USE_SSL：端口号465
# QQ邮箱不支持非加密方式发送邮件
# 发送者邮箱的服务器地址
app.config['MAIL_SERVER'] = "smtp.qq.com"
app.config['MAIL_PORT'] = '587'
app.config['MAIL_USE_TLS'] = True
# MAIL_USE_SSL
app.config['MAIL_USERNAME'] = "2406812549@qq.com"
app.config['MAIL_PASSWORD'] = "anpykzzdxbdrdhfj"  # 生成授权码，授权码是开启smtp服务后给出的
app.config['MAIL_DEFAULT_SENDER'] = "2406812549@qq.com"


# 缓存
app.config['CACHE_TYPE'] = 'simple'  # 本地缓存，一级缓存，缓存量大的情况下需使用二级缓存，一般使用redis
app.config['CACHE_DEFAULT_TIMEOUT'] = 60 * 5  # 默认过期时间 5分钟
cache.init_app(app)