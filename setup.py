from setuptools import setup

setup(name='tableau-backup',
      version='0.1',
      description='Tool to backup Tableau site to S3 as a ZIP file',
      url='',
      author='Andres Recalde',
      author_email='andres@lacolombe.com',
      license='MIT',
      packages=['tableau-backup'],
      install_requires=[
          'tableauserverclient',
          'boto3',
      ],
      zip_safe=False)