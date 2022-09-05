from logstash import TCPLogstashHandler


class StrTCPLogstashHandler(TCPLogstashHandler):
    def makePickle(self, record):
        return str.encode(self.formatter.format(record)) + b'\n'
