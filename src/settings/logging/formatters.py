import json_log_formatter


class LogstashJSONFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra['module'] = record.name
        return extra
