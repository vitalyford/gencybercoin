from storages.backends.s3boto3 import S3Boto3Storage


class S3CustomMediaStorage(S3Boto3Storage):
    def _normalize_name(self, name):
        # get rid of this: https://stackoverflow.com/questions/12535123/django-storages-and-amazon-s3-suspiciousoperation
        return name


StaticRootS3BotoStorage = lambda: S3Boto3Storage(location='static')
MediaRootS3BotoStorage  = lambda: S3CustomMediaStorage(location='media')
