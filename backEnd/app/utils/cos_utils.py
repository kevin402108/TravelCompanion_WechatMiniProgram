import os
from typing import Optional, Tuple, Dict, Any, List

from dotenv import load_dotenv
from qcloud_cos import CosConfig, CosS3Client
from qcloud_cos.cos_comm import format_region

from backEnd.app.utils.logger import setup_logger

# 日志记录器
tencentcloud_cos_logger = setup_logger('tencentcloud_cos_logger', 'tencentcloud_cos.log')

# 加载环境变量
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOTENV_PATH = os.path.join(ROOT_DIR, ".env")
if not os.path.exists(DOTENV_PATH):
    error_msg = f"无法找到 .env 文件"
    tencentcloud_cos_logger.warning( error_msg )
else:
    tencentcloud_cos_logger.warning( "加载.env文件成功" )
    load_dotenv(DOTENV_PATH)

class TencentCloudCOSManager:
    def __init__(self, bucket_name: Optional[str] = None):
        """
        初始化腾讯云COS管理器
        :param bucket_name: 存储桶名称，可选参数，默认为None
        """
        if bucket_name is not None and not isinstance(bucket_name, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager __init__] bucket_name参数必须是字符串")
            raise ValueError("bucket_name参数不为None但不是字符串类型")

        # 从环境变量获取配置
        self.secret_id = os.getenv('COS_SECRET_ID')
        self.secret_key = os.getenv('COS_SECRET_KEY')
        self.region = os.getenv('COS_REGION')
        self.domain = os.getenv('COS_DOMAIN')
        self.bucket_name = bucket_name
        self.schema = 'https'

        # 检查必需的环境变量
        missing_vars = []
        required_vars = ['COS_SECRET_ID', 'COS_SECRET_KEY', 'COS_REGION', 'COS_DOMAIN']
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            error_msg = f"缺少环境变量: {', '.join(missing_vars)}"
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager __init__] {error_msg}")
            raise ValueError(error_msg)

        # 初始化COS配置
        try:
            token = None
            self.config = CosConfig(
                Region=self.region,
                SecretId=self.secret_id,
                SecretKey=self.secret_key,
                Token=token,
            )
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager __init__] COS配置初始化失败: {str(e)}")
            raise RuntimeError(f"COS配置初始化失败: {str(e)}")

        # 初始化COS客户端
        try:
            self.client = CosS3Client(self.config)
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager __init__] COS客户端初始化失败: {str(e)}")
            raise RuntimeError(f"COS客户端初始化失败: {str(e)}")

        tencentcloud_cos_logger.info(f"[TencentCloudCOSManager __init__] 初始化腾讯云COS管理器成功")

    # 存储桶相关操作
    def list_buckets(self) -> Tuple[bool, Dict[str, Any]]:
        """列出所有存储桶"""
        try:
            response = self.client.list_buckets()
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager list_buckets] 存储桶列表获取成功")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager list_buckets] 存储桶列表获取失败: {str(e)}")
            return False, {"error": str(e)}

    def set_bucket(self, bucket_name: str) -> bool:
        """设置存储桶名称"""
        if not isinstance(bucket_name, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager set_bucket] bucket_name参数必须是字符串")
            return False
        if not bucket_name:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager set_bucket] bucket_name参数不能为空")
            return False
        try:
            self.bucket_name = bucket_name
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager set_bucket] 存储桶名称设置成功: {self.bucket_name}")
            return True
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager set_bucket] 存储桶名称设置失败: {str(e)}")
            return False

    def create_bucket(self, bucket_name: Optional[str] = None, acl: str = 'private') -> Tuple[bool, Dict[str, Any]]:
        """创建存储桶"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager create_bucket] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(bucket, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager create_bucket] 存储桶名称必须是字符串")
            return False, {"error": "bucket_name必须是字符串"}
        if acl not in ['private', 'public-read', 'public-read-write']:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager create_bucket] ACL参数错误")
            return False, {"error": "ACL参数必须是 'private', 'public-read', 'public-read-write' 中的一个"}

        try:
            response = self.client.create_bucket(
                Bucket=bucket,
                ACL=acl
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager create_bucket] 创建存储桶成功: {bucket}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager create_bucket] 创建存储桶失败: {str(e)}")
            return False, {"error": str(e)}

    def delete_bucket(self, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """删除存储桶"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager delete_bucket] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}

        try:
            response = self.client.delete_bucket(
                Bucket=bucket
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager delete_bucket] 存储桶删除成功: {bucket}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager delete_bucket] 存储桶删除失败: {str(e)}")
            return False, {"error": str(e)}

    def bucket_exists(self, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """判断存储桶是否存在"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager bucket_exists] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}

        try:
            response = self.client.head_bucket(Bucket=bucket)
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager bucket_exists] 存储桶存在: {bucket}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager bucket_exists] 存储桶不存在: {str(e)}")
            return False, {"error": str(e)}

    def head_bucket(self, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """检索存储桶是否存在且是否有权限访问"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager head_bucket] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}

        try:
            response = self.client.head_bucket(
                Bucket=bucket
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager head_bucket] 存储桶存在: {bucket}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager head_bucket] 存储桶不存在: {str(e)}")
            return False, {"error": str(e)}

    # 存储对象操作
    def upload_file(self, local_file_path: str, cos_key: str, bucket_name: Optional[str] = None, enable_md5: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """上传文件到COS"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager upload_file] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(local_file_path, str) or not isinstance(cos_key, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager upload_file] 参数类型错误")
            return False, {"error": "参数类型错误"}
        if not os.path.exists(local_file_path):
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager upload_file] 本地文件不存在: {local_file_path}")
            return False, {"error": "本地文件不存在"}

        try:
            response = self.client.upload_file(
                Bucket=bucket,
                Key=cos_key,
                LocalFilePath=local_file_path,
                EnableMD5=enable_md5
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager upload_file] 文件上传成功: {cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager upload_file] 文件上传失败: {str(e)}")
            return False, {"error": str(e)}

    def download_file( self , cos_key: str , dest_file_path: str , bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any ] ]:
        """从COS下载文件"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager download_file] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(cos_key, str) or not isinstance(dest_file_path, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager download_file] 参数类型错误")
            return False, {"error": "参数类型错误"}

        try:
            response = self.client.download_file(
                Bucket=bucket,
                Key=cos_key,
                DestFilePath=dest_file_path
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager download_file] 文件下载成功: {cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager download_file] 文件下载失败: {str(e)}")
            return False, {"error": str(e)}

    def copy_object(self, source_cos_key: str, dest_cos_key: str, source_bucket: Optional[str] = None, dest_bucket: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """复制对象"""
        src_bucket = source_bucket or self.bucket_name
        dst_bucket = dest_bucket or self.bucket_name
        if not src_bucket or not dst_bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager copy_object] 源或目标存储桶名称不能为空")
            return False, {"error": "源或目标bucket_name不能为空"}
        if not isinstance(source_cos_key, str) or not isinstance(dest_cos_key, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager copy_object] 参数类型错误")
            return False, {"error": "参数类型错误"}

        copy_source = {
            "Bucket": src_bucket,
            "Key": source_cos_key,
            "Region": self.region,
            # "VersionId": "null"
        }
        try:
            response = self.client.copy(
                Bucket=dst_bucket,
                Key=dest_cos_key,
                CopySource=copy_source
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager copy_object] 对象复制成功: {source_cos_key} -> {dest_cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager copy_object] 对象复制失败: {str(e)}")
            return False, {"error": str(e)}

    def delete_file(self, cos_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """删除COS中的文件"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager delete_file] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(cos_key, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager delete_file] 参数类型错误")
            return False, {"error": "参数类型错误"}

        try:
            response = self.client.delete_object(
                Bucket=bucket,
                Key=cos_key
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager delete_file] 文件删除成功: {cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager delete_file] 文件删除失败: {str(e)}")
            return False, {"error": str(e)}

    def object_exists(self, cos_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """判断对象是否存在"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager object_exists] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}

        try:
            response = self.client.object_exists(
                Bucket=bucket,
                Key=cos_key
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager object_exists] 对象存在: {cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager object_exists] 获取对象失败: {str(e)}")
            return False, {"error": str(e)}

    def list_files(self, prefix: str = "", max_keys: int = 1000, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """列出存储桶中的文件"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager list_files] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(prefix, str) or not isinstance(max_keys, int):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager list_files] 参数类型错误")
            return False, {"error": "参数类型错误"}

        try:
            response = self.client.list_objects(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager list_files] 文件列表获取成功")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager list_files] 文件列表获取失败: {str(e)}")
            return False, {"error": str(e)}

    def get_file_info(self, cos_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """获取文件信息"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_file_info] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(cos_key, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_file_info] 参数类型错误")
            return False, {"error": "参数类型错误"}

        try:
            response = self.client.head_object(
                Bucket=bucket,
                Key=cos_key
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager get_file_info] 文件信息获取成功: {cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager get_file_info] 文件信息获取失败: {str(e)}")
            return False, {"error": str(e)}

    def restore_object(self, cos_key: str, days: int = 1, tier: str = 'Expedited', bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """恢复归档对象"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager restore_object] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(cos_key, str) or not isinstance(days, int):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager restore_object] 参数类型错误")
            return False, {"error": "参数类型错误"}
        if tier not in ['Expedited', 'Standard', 'Bulk']:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager restore_object] tier参数错误")
            return False, {"error": "tier参数必须是 'Expedited', 'Standard', 'Bulk' 中的一个"}

        try:
            response = self.client.restore_object(
                Bucket=bucket,
                Key=cos_key,
                RestoreRequest={
                    'Days': days,
                    'CASJobParameters': {
                        'Tier': tier
                    }
                }
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager restore_object] 对象恢复请求成功: {cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager restore_object] 对象恢复请求失败: {str(e)}")
            return False, {"error": str(e)}

    def get_presigned_url(self, cos_key: str, method: str = 'get', expires: int = 3600, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """获取预签名URL"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_presigned_url] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(cos_key, str) or not isinstance(method, str) or not isinstance(expires, int):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_presigned_url] 参数类型错误")
            return False, {"error": "参数类型错误"}
        if method.lower() not in ['get', 'post', 'put', 'delete']:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_presigned_url] HTTP方法错误")
            return False, {"error": "HTTP方法必须是 'get', 'post', 'put', 'delete' 中的一个"}

        try:
            url = self.client.get_presigned_url(
                Bucket=bucket,
                Key=cos_key,
                Method=method.upper(),
                Expired=expires
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager get_presigned_url] 预签名URL生成成功: {cos_key}")
            return True, {"url": url}
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager get_presigned_url] 预签名URL生成失败: {str(e)}")
            return False, {"error": str(e)}

    # 权限管理
    def set_bucket_acl(self, acl: str = 'private', bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """设置存储桶访问权限"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager set_bucket_acl] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if acl not in ['private', 'public-read', 'public-read-write']:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager set_bucket_acl] ACL参数错误")
            return False, {"error": "ACL参数必须是 'private', 'public-read', 'public-read-write' 中的一个"}

        try:
            response = self.client.put_bucket_acl(
                Bucket=bucket,
                ACL=acl
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager set_bucket_acl] 存储桶权限设置成功: {acl}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager set_bucket_acl] 存储桶权限设置失败: {str(e)}")
            return False, {"error": str(e)}

    def get_bucket_acl(self, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """获取存储桶访问权限"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_bucket_acl] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}

        try:
            response = self.client.get_bucket_acl(
                Bucket=bucket
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager get_bucket_acl] 存储桶权限获取成功")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager get_bucket_acl] 存储桶权限获取失败: {str(e)}")
            return False, {"error": str(e)}



    def set_object_acl(self, cos_key: str, acl: str = 'private', bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """设置对象访问权限"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager set_object_acl] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(cos_key, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager set_object_acl] 参数类型错误")
            return False, {"error": "参数类型错误"}
        if acl not in ['private', 'public-read', 'public-read-write']:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager set_object_acl] ACL参数错误")
            return False, {"error": "ACL参数必须是 'private', 'public-read', 'public-read-write' 中的一个"}

        try:
            response = self.client.put_object_acl(
                Bucket=bucket,
                Key=cos_key,
                ACL=acl
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager set_object_acl] 对象权限设置成功: {cos_key}, {acl}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager set_object_acl] 对象权限设置失败: {str(e)}")
            return False, {"error": str(e)}

    def get_object_acl(self, cos_key: str, bucket_name: Optional[str] = None) -> Tuple[bool, Dict[str, Any]]:
        """获取对象访问权限"""
        bucket = bucket_name or self.bucket_name
        if not bucket:
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_object_acl] 存储桶名称不能为空")
            return False, {"error": "bucket_name不能为空"}
        if not isinstance(cos_key, str):
            tencentcloud_cos_logger.error("[TencentCloudCOSManager get_object_acl] 参数类型错误")
            return False, {"error": "参数类型错误"}

        try:
            response = self.client.get_object_acl(
                Bucket=bucket,
                Key=cos_key
            )
            tencentcloud_cos_logger.info(f"[TencentCloudCOSManager get_object_acl] 对象权限获取成功: {cos_key}")
            return True, response
        except Exception as e:
            tencentcloud_cos_logger.error(f"[TencentCloudCOSManager get_object_acl] 对象权限获取失败: {str(e)}")
            return False, {"error": str(e)}


