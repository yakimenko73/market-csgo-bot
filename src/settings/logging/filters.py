from logging import Filter, LogRecord


class SkipStaticFilter(Filter):
    def filter(self, record: LogRecord):
        return not (record.getMessage().startswith('"GET /static/')
                    or record.getMessage().startswith('"GET /admin/jsi18n'))
