"""Utility module providing I/O related classes and functions."""

from io import StringIO


class TeeStringIO:
    """String IO implementation that captures output while preserving original logger output."""

    def __init__(self, logger_output):
        """Initialize a TeeStringIO instance.

        Args:
            logger_output: A callable that will receive captured output.
        """
        self.logger_output = logger_output
        self.buffer = StringIO()

    def write(self, value):
        """Write a string to both the logger and internal buffer.

        Args:
            value: The string to write.
        """
        self.logger_output(value.strip("\n"))
        self.buffer.write(value)

    def read(self):
        """Read the contents of the buffer.

        Returns:
            The buffer contents as a string.
        """
        return self.buffer.read()

    def seek(self, *args, **kwargs):
        """Set the buffer's position.

        Args:
            *args: Positional arguments passed to the underlying buffer.
            **kwargs: Keyword arguments passed to the underlying buffer.

        Returns:
            The new position in the buffer.
        """
        return self.buffer.seek(*args, **kwargs)

    def flush(self):
        """Flush the internal buffer."""
        self.buffer.flush()
