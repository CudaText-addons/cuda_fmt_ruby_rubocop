import os
from subprocess import Popen, PIPE
from cuda_fmt import get_config_filename
from cuda_fmt import fmtconfig 

import logging
log = logging.getLogger('root')


def get_cmd():
    interpreter = 'ruby'
    executable = 'rubocop'

    #cmd = [interpreter, executable]
    cmd = [executable]

    cmd.extend(['--config', get_config_filename('Ruby Rubocop')])
    cmd.extend(['--stdin', '-', '--auto-correct'])

    return cmd


def exec_cmd(cmd, path):
    IS_WINDOWS = os.name=='nt'
    if IS_WINDOWS:
        from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW, SW_HIDE
        # Hide the console window
        info = STARTUPINFO()
        info.dwFlags |= STARTF_USESHOWWINDOW
        info.wShowWindow = SW_HIDE
    else:
        info = None

    process = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, 
                    cwd=path,
                    #env=update_environ(),
                    shell=IS_WINDOWS,
                    startupinfo=info
                    )
    return process


def do_format(text):
    filename = fmtconfig.ed_filename
    cmd = get_cmd()

    try:
        proc = exec_cmd(cmd, os.path.dirname(filename))
        stdout, stderr = proc.communicate(text.encode('utf-8'))

        errno = proc.returncode
        if errno > 1:
            log.error('File not formatted due to an error (errno=%d): "%s"', errno, stderr.decode('utf-8'))
        else:
            if errno == 1:
                log.warning('Inconsistencies occurred (errno=%d): "%s"', errno, stderr.decode('utf-8'))

            string = stdout.decode('utf-8')
            print(string)###
            result = string.split('====================\n')
            if len(result) == 2:
                return result[1]
            result = string.split('====================\r\n')
            if len(result) == 2:
                return result[1]
    except OSError:
        log.error('Error occurred when running: %s', ' '.join(cmd))
