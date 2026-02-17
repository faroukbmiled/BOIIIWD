# Linux PTY process wrapper using pexpect
import pexpect
import fcntl
import os
import select


class PtyProcess:
    """PTY wrapper using pexpect for Linux."""

    def __init__(self, process):
        self._process = process
        self.flag_eof = False

    @classmethod
    def spawn(cls, command, cwd=None, env=None, dimensions=(24, 80)):
        """Spawn a new process in a PTY."""
        if isinstance(command, list):
            cmd = command[0]
            args = command[1:]
        else:
            cmd = command
            args = []

        process = pexpect.spawn(
            cmd,
            args=args,
            cwd=cwd,
            env=env,
            dimensions=dimensions,
            encoding='utf-8',
            timeout=None
        )

        # Set non-blocking mode
        fd = process.child_fd
        flags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        return cls(process)

    def nb_read(self, size=1024):
        """Non-blocking read from the PTY."""
        if self.flag_eof:
            raise EOFError("Pty is closed")

        try:
            r, _, _ = select.select([self._process.child_fd], [], [], 0)
            if not r:
                return ""

            data = self._process.read_nonblocking(size, timeout=0)
            return data if data else ""
        except pexpect.EOF:
            self.flag_eof = True
            raise EOFError("Pty is closed")
        except pexpect.TIMEOUT:
            return ""
        except Exception:
            return ""

    def read(self, size=1024):
        """Blocking read from the PTY."""
        try:
            return self._process.read(size)
        except pexpect.EOF:
            self.flag_eof = True
            raise EOFError("Pty is closed")

    def write(self, data):
        """Write data to the PTY."""
        if isinstance(data, str):
            self._process.send(data)
        else:
            self._process.send(data.decode('utf-8'))

    def isalive(self):
        """Check if the process is still running."""
        return self._process.isalive()

    def terminate(self, force=False):
        """Terminate the process."""
        self._process.terminate(force=force)

    def close(self):
        """Close the PTY."""
        self._process.close()

    def wait(self):
        """Wait for the process to finish."""
        self._process.wait()

    @property
    def exitstatus(self):
        return self._process.exitstatus

    @property
    def pid(self):
        return self._process.pid
