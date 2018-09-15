# coding=utf-8
"""
Miktex external tool
"""

import typing
from pathlib import Path

import elib

from edlm import HERE
from edlm.external_tools.base import BaseExternalTool

StrOrPath = typing.Union[str, Path]

MPM_CONFIG = """;;; DO NOT EDIT THIS FILE!


[MPM]
AutoInstall=1

"""


class MikTex(BaseExternalTool):
    """
    Miktex external tool
    """

    @property
    def url(self) -> str:
        """Download URL"""
        return r'https://www.dropbox.com/s/ivyb6s5itb5len2/miktex.7z?dl=1'

    @property
    def hash(self) -> str:
        """Expected archive hash"""
        return 'fc20affd161264e7c5b816ddc85955cd'

    @property
    def default_archive(self) -> Path:
        """Expected tool version"""
        return Path('./miktex.7z').absolute()

    @property
    def default_install(self) -> Path:
        """Default installation location"""
        return Path('./tools/miktex').absolute()

    @property
    def expected_version(self) -> str:
        """Expected tool version"""
        return '2.9.6354'

    def get_version(self) -> str:
        """
        Returns: Miktex version
        """
        return self('--version').split('\n')[0].split(' ')[1]

    def get_exe(self) -> Path:
        """
        Returns: Miktex executable
        """
        return Path(self.install_dir, 'texmfs/install/miktex/bin/pdflatex.exe').absolute()

    @staticmethod
    def _create_new_mpm_settings_file(mpm_config_file):
        elib.path.ensure_dir(mpm_config_file.parent, must_exist=False, create=True)
        mpm_config_file.write_text(MPM_CONFIG, encoding='utf8')

    @staticmethod
    def _edit_auto_install_line(content):
        for index, line in enumerate(content):
            if 'AutoInstall=' in line:
                content[index] = 'AutoInstall=1'
                return True
        return False

    @staticmethod
    def _add_auto_install_line(content: list):
        for index, line in enumerate(content):
            if '[MPM]' in line:
                content.insert(index + 1, 'AutoInstall=1')
                return True
        return False

    @staticmethod
    def _add_mpm_section(content: list):
        content.append('[MPM]')
        content.append('AutoInstall=1\n')
        return True

    def _edit_existing_mpm_settings_file(self, mpm_config_file):
        content = mpm_config_file.read_text(encoding='utf8').split('\n')
        func_list = [self._edit_auto_install_line, self._add_auto_install_line, self._add_mpm_section]
        for func in func_list:  # pragma: no cover
            if func(content):
                mpm_config_file.write_text('\n'.join(content))
                return

    def _write_mpm_settings_file(self):
        mpm_config_file = Path(self.install_dir, 'texmfs/config/miktex/config/miktex.ini')
        if not mpm_config_file.exists():
            self._create_new_mpm_settings_file(mpm_config_file)
        else:
            self._edit_existing_mpm_settings_file(mpm_config_file)

    def setup(self):
        """
        Setup Miktex
        """
        super(MikTex, self).setup()
        self._write_mpm_settings_file()
