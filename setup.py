from setuptools import setup


SHORT_DESCRIPTION = 'Preprocessor for Foliant for generating history of releases.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='foliantcontrib.history',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='1.0.8',
    author='Artemy Lomov',
    author_email='artemy@lomov.ru',
    url='https://github.com/foliant-docs/foliantcontrib.history',
    packages=['foliant.preprocessors'],
    license='MIT',
    platforms='any',
    install_requires=[
        'foliant>=1.0.10',
        'foliantcontrib.includes>=1.1.6',
        'Markdown'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ]
)
