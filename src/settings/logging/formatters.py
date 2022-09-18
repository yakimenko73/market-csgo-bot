from json_log_formatter import JSONFormatter


class LogstashJSONFormatter(JSONFormatter):
    def json_record(self, message, extra, record):
        extra['module'] = record.name

        return super().json_record(message, extra, record)
