from qiniu import Auth, put_data
from flask import current_app


def pic1(f1):
    # 需要填写你的 Access Key 和 Secret Key
    access_key = current_app.config.get('QINIU_AK')
    secret_key = current_app.config.get('QINIU_SK')
    # 空间名称
    bucket_name = current_app.config.get('QINIU_BUCKET')
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 生成上传 Token
    token = q.upload_token(bucket_name)
    # 上传文件数据，ret是字典，键为hash、key，值为新文件名，info是response对象
    ret, info = put_data(token, None, f1.read())
    # 返回七牛云给出的文件名
    return ret.get('key')
