import os.path

try:
    from setuptools import find_packages, setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import find_packages, setup


def readme():
    try:
        with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
            return f.read()
    except (IOError, OSError):
        return ''


setup_requires = [
    'py2app >= 0.8'
]

install_requires = [
    'libearth == 0.3.0',
    'pyobjc == 2.5.1',
    'pyobjc-framework-Cocoa == 2.5.1',
    'pyobjc-framework-WebKit == 2.5.1',
    'Jinja2 == 2.7.2'
]


setup(
    name='EarthReader-Mac',
    version='0.1.0',  # FIXME
    description='Earth Reader for Mac',
    long_description=readme(),
    url='http://earthreader.org/',
    author='Earth Reader team',
    author_email='earthreader' '@' 'librelist.com',
    license='GPLv3 or later',
    packages=find_packages(),
    data_files=['earthreader/mac/MainWindow.xib'],
    app=['EarthReader.py'],
    options={
        'py2app': {
            'iconfile': 'icon.ics',
            'frameworks': 'WebKit',
            'plist': {
                'CFBundleName': 'Earth Reader',
                'CFBundleIdentifier': 'org.earthreader.mac.EarthReader'
            }
        }
    },
    setup_requires=setup_requires,
    install_requires=install_requires,
    dependency_links=[
        'https://github.com/earthreader/libearth/releases'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: MacOS X :: Cocoa',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved ::'
        ' GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Objective C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Communications',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
        'Topic :: Text Processing :: Markup :: XML'
    ]
)
