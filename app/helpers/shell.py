import os

from netmiko import ConnectHandler, NetmikoTimeoutException


SSH_USERNAME = os.environ.get('SSH_USERNAME')
SSH_PASSWORD = os.environ.get('SSH_PASSWORD')
SSH_PORT = os.environ.get('SSH_PORT')
SSH_HOST = os.environ.get('SSH_HOST')

DENY_LIST = os.environ.get('DENY_LIST')
PERMIT_LIST = os.environ.get('PERMIT_LIST')
PERMANENT_BAN_LIST = os.environ.get('PERMANENT_BAN_LIST')
BAN_TIMEOUT = os.environ.get('BAN_TIMEOUT', '00:30:00')
VPN_SERVER = os.environ.get('VPN_SERVER')


def _configure_connection_settings() -> None:
    router = {
        'device_type': 'mikrotik_routeros',
        'host': SSH_HOST,
        'username': SSH_USERNAME,
        'password': SSH_PASSWORD,
        'port': SSH_PORT,
        'global_delay_factor': 2,
    }
    return router


def authorize_ip_address(source_ip: str) -> bool:
    router = _configure_connection_settings()
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False

    ssh.send_command(f'ip firewall address-list remove [find address={source_ip} list={DENY_LIST}]')
    ssh.send_command(f'ip firewall address-list add list={PERMIT_LIST} address={source_ip} comment="vpn user"')
    return True


def ban_ip_address(source_ip: str, caller_id: str) -> bool:
    router = _configure_connection_settings()
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False

    ssh.send_command(f'ip firewall address-list remove [find address={source_ip} list={DENY_LIST}]')
    ssh.send_command(f'ip firewall address-list add list={PERMANENT_BAN_LIST} address={caller_id} timeout={BAN_TIMEOUT} comment="vpn user"')
    ssh.send_command(f'[/interface {VPN_SERVER}-server remove [find where client-address={caller_id}]]')
    ssh.disconnect()
    return True


def unban_ip_address(caller_id: str or list) -> bool:
    router = _configure_connection_settings()
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False
    if isinstance(caller_id, list):
        for ip in caller_id:
            ssh.send_command(f'[/ip firewall address-list remove [find address={ip} list={PERMANENT_BAN_LIST}]]')
    else:
        ssh.send_command(f'[/ip firewall address-list remove [find address={caller_id} list={PERMANENT_BAN_LIST}]]')
    ssh.disconnect()
    return True


def disconnect_client(caller_id: str or list) -> bool:
    router = _configure_connection_settings()
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False
    if isinstance(caller_id, list):
        for ip in caller_id:
            cmd = f'[/interface {VPN_SERVER}-server remove [find where client-address={ip}]]'
            ssh.send_command(cmd)
    else:
        cmd = f'[/interface {VPN_SERVER}-server remove [find where client-address={caller_id}]]'
        ssh.send_command(cmd)
    ssh.disconnect()
    return True