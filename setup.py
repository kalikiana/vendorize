#!/usr/bin/env python3
# -*- mode: python; -*-
#
# Copyright 2018 Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This package is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
vendorizer
==========
A given snap will be prepared to vendorize all dependencies pulled
in from sources outside the allowed hosts effectively creating stable
branches to make rebuilds safe.
"""

from setuptools import setup, find_packages

setup(name='vendorize',
      version='0.1',
      description="Vendorize snap",
      long_description=__doc__,
      author='Canonical Engineering',
      author_email='ubuntu-dev@lists.ubuntu.com',
      url='https://github.com/kalikiana/vendorize',
      license='GPL v3+',
      packages=find_packages(exclude=["tests"]))
