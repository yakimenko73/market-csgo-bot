from logging import LogRecord

from logstash import TCPLogstashHandler


class StrTCPLogstashHandler(TCPLogstashHandler):
    def makePickle(self, record: LogRecord):
        return str.encode(self.formatter.format(record)) + b'\n'
