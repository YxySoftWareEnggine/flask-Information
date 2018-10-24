from qiniu import Auth,etag,put_file,put_data
import logging

access_key = "wGFdWHfN827S1hq5UUIag1sg5rkwvpDgVfr4VRkR"
secret_key = "5qlDrPckQIUkfSpOzVxNhJLMoFmRqzYZx26rfpgT"
bucket_name = "infomation"

def Stroge(data):
    if not data:
        return None
    try:
        # 构建鉴权对象
        q = Auth(access_key, secret_key)

        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name)
        # 上传文件
        ret, info = put_data(token,None,data)#(token,None,data)

    except Exception as e:
        logging.error(e)
        raise e

    if info and info.status_code != 200:
        raise Exception("上传文件到七牛失败")

        # 返回七牛中保存的图片名，这个图片名也是访问七牛获取图片的路径
    return ret["key"]
