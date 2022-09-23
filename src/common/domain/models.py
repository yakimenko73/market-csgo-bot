from pydantic import BaseModel
from python_socks import ProxyType


class ProxyCredentials(BaseModel):
    proxy_type: ProxyType
    host: str
    port: int
    username: str
    password: str

    @staticmethod
    def parse_str(raw_str: str, proxy_type: ProxyType = ProxyType.SOCKS5):
        host, port, username, password = raw_str.split(':')
        return ProxyCredentials(
            proxy_type=proxy_type.value,
            host=host,
            port=port,
            username=username,
            password=password
        )
