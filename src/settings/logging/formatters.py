from json_log_formatter import JSONFormatter


class LogstashJSONFormatter(JSONFormatter):
    def json_record(self, message, extra, record):
        extra['module'] = record.name
        extra['log_level'] = record.levelname

        return super().json_record(message, extra, record)
