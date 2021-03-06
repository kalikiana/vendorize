import os
import setuptools
import subprocess
import shutil


import vendorize.plugin
import vendorize.util


class Python(vendorize.plugin.Plugin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.python_cache = os.path.join(self.part_dir, 'python-packages')

    def process(self):
        os.makedirs(self.python_cache, exist_ok=True)
        self.download_packages(self.get_packages())
        self.unpack_archives()
        self.prepare_branches()

    def get_packages(self) -> list:
        python_packages = self.data.get('python-packages', [])
        requirements = self.data.get('requirements')
        if requirements:
            path = os.path.join(self.part_dir, 'src', requirements)
            if not os.path.exists(path):
                raise vendorize.plugin.PluginError(
                    'External requirements are not supported')
            with open(path) as r:
                for line in r:
                    package = line.strip()
                    # A leading # is a comment, otherwise it's part of a URL
                    if not package.startswith('#'):
                        python_packages.append(package)
        for package in self.packages_from_setup_py():
            python_packages.append(package)
        return python_packages

    def download_packages(self, python_packages: list):
        # Download packages one by one so that errors related to build
        # dependencies that we don't care about here can be safely ignored.
        self.debug('Fetching: {}'.format(', '.join(python_packages)))
        for package in python_packages:
            # Downloaded wheels/ archives are saved to the current folder
            try:
                subprocess.check_call([
                    'python3', '-m', 'pip',
                    'download', '--no-binary=:all:', '-q',
                    '--exists-action=i',  # ignore
                    '--dest={}'.format(self.python_cache),
                    '--src={}'.format(self.python_cache)] +
                    package.split(' '))
            except subprocess.CalledProcessError as e:
                # Errors in setup.py due to for example pkg-config being run
                # can be ignored since we're not looking to build anything.
                self.debug('Error during download: {!r}'.format(e))

    def unpack_archives(self):
        # Unpack all archives, skip folders of "editable" packages.
        python_packages = [
            d for d in os.listdir(self.python_cache)
            if not os.path.isdir(os.path.join(self.python_cache, d))]
        self.debug('Extracting: {}'.format(', '.join(python_packages)))
        for package in python_packages:
            filename = os.path.join(self.python_cache, package)
            # The archive's root folder is the package name
            shutil.unpack_archive(filename, self.python_cache)

    def prepare_branches(self):
        # Prepare a branch for each folder
        branches = []  # type: list
        sources = [
            d for d in os.listdir(self.python_cache)
            if os.path.isdir(os.path.join(self.python_cache, d))]
        self.debug('Branching: {}'.format(', '.join(sources)))
        for package in sources:
            copy = os.path.join(self.python_cache, package)
            path = [self.part, 'python_packages', package]
            branches.append('git+{}'.format(self.processor.prepare_source(
                path, copy, init=True,
                commit='Vendor {}'.format(package))))
        filename = os.path.join(self.copy, 'requirements.txt')
        with open(filename, 'w') as f:
            for requirement in branches:
                f.write('{}\n'.format(requirement))
        self.data['requirements'] = 'requirements.txt'
        if 'python-packages' in self.data:
            del self.data['python-packages']

    def packages_from_setup_py(self):
        setup_py = os.path.join(self.source, 'setup.py')
        if not os.path.exists(setup_py):
            return []

        # Try and use setuptools to get install_requires
        def setup(*args, **kwargs):
            globals()['metadata'] = kwargs
        setuptools.setup = setup
        try:
            with open(setup_py) as f:
                with vendorize.util.chdir(self.source):
                    exec(f.read())
                    metadata = globals()['metadata']
                    return metadata.get('install_requires', [])
        except Exception as e:
            self.debug(
                'Failed to parse {!r}: {}'.format(setup_py, e))
            return []
