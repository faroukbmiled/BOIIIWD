# Monkey patching winpty to add a custom non-blocking output reader function (nb_read)
# This function uses select to avoid blocking if there's no data to read.

import select
from winpty import PtyProcess as OriginalPtyProcess


class PatchedPtyProcess(OriginalPtyProcess):
    def nb_read(self, size: int = 1024) -> str:
        """Read and return at most ``size`` characters from the pty.

        Uses select to avoid blocking if there's no data to read.
        Raises :exc:`EOFError` if the terminal was closed.
        """
        ...


def nb_read(self, size=1024):
    """Read and return at most ``size`` characters from the pty.

    Uses select to avoid blocking if there's no data to read.
    Raises :exc:`EOFError` if the terminal was closed.
    """
    r, _, _ = select.select([self.fileobj], [], [], 0)
    if not r:
        return ""

    data = self.fileobj.recv(size)
    if not data:
        self.flag_eof = True
        raise EOFError("Pty is closed")

    if data == b"0011Ignore":
        data = ""

    err = True
    while err and data:
        try:
            data.decode("utf-8")
            err = False
        except UnicodeDecodeError:
            data += self.fileobj.recv(1)
    return data.decode("utf-8")


OriginalPtyProcess.nb_read = nb_read
PtyProcess: PatchedPtyProcess = OriginalPtyProcess
