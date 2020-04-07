import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'koolstof',
    version = '0.0.1',
    author = 'Matthew P. Humphreys',
    author_email = 'm.p.humphreys@icloud.com',
    description = 'Miscellaneous tools for marine carbonate chemistry',
    url = 'https://github.com/mvdh7/koolstof',
    packages = setuptools.find_packages(),
    install_requires = [],
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    classifiers = [
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Chemistry',
    ],
)
