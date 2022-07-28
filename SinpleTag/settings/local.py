from .base import *
import environ

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)


# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# False if not in os.environ because of casting above
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': env.db(),

    'extra': env.db_url(
        'SQLITE_URL',
        default='sqlite:///tmp/my-tmp-sqlite.db'
    )
}
