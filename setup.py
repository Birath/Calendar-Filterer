from setuptools import setup

setup(
    name='calendar-filterer',
    packages=['app'],
    include_package_data=True,
    install_requires=[
        'flask',
        'icalendar',
        'requests',
        'google-api-python-client',
        'google-auth',
        'google-auth-oauthlib',
        'google-auth-httplib2', 'celery'
    ]
)