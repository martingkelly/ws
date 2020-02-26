#!/usr/bin/python3
#
# setuptools builder.
#
# Copyright (c) 2018-2019 Xevo Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
from wst import (
    DEFAULT_TARGETS,
    WSError
)
from wst.builder import Builder
from wst.shell import (
    call_build,
    rmtree
)


class SetuptoolsBuilder(Builder):
    '''A setuptools builder.'''

    import sysconfig
    _SITE_PACKAGES_DIR = sysconfig.get_paths()['purelib']

    @classmethod
    def env(cls, proj, prefix, build_dir, env):
        '''Sets up environment tweaks for setuptools.'''
        # Import here to prevent a circular import.
        from wst.conf import merge_var

        # setuptools won't install into a --prefix unless the site-packages
        # directory is in PYTHONPATH, so we'll add it in manually.
        python_path = os.path.join(prefix, cls._SITE_PACKAGES_DIR)
        merge_var(env, 'PYTHONPATH', [python_path])

    @classmethod
    def conf(cls,
             proj,
             prefix,
             source_dir,
             build_dir,
             env,
             build_type,
             args):
        '''Calls configure using setuptools.'''
        # setuptools doesn't have a configure step.
        return True

    @classmethod
    def build(cls, proj, prefix, source_dir, build_dir, env, targets, args):
        '''Calls build using setuptools.'''
        if targets is not None and targets != DEFAULT_TARGETS:
            raise WSError('pip3 does not support alternate build targets but '
                          '"%s" was specified for targets' % targets)
        cmd = ['pip3',
               'install',
               '--prefix=%s' % prefix,
               '--build=%s' % build_dir]
        cmd.extend(args)
        cmd.append('.')
        return call_build(cmd, cwd=source_dir, env=env)

    @classmethod
    def clean(cls, proj, prefix, source_dir, build_dir, env):
        '''Calls clean using setuptools.'''
        # setuptools appears not to have a nicer way to do a "make clean" on a
        # dev-installed package.
        rmtree(build_dir)
