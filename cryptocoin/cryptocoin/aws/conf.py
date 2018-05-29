import datetime
AWS_ACCESS_KEY_ID = "AKIAIVVFS7V7EOK3BGRQ"
AWS_SECRET_ACCESS_KEY = "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"
AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = True

DEFAULT_FILE_STORAGE = 'cryptocoin.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'cryptocoin.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'gencybercoin-bucket'
S3DIRECT_REGION = 'us-east-1'
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'gcsuperuser/'

one_day = datetime.timedelta(days=1)
date_one_day_later = datetime.date.today() + one_day
expires = date_one_day_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    'Expires': expires,
    'Cache-Control': 'max-age=86400',
}
