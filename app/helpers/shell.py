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


def ban_ip_address(source_ip: str) -> bool:
    router = _configure_connection_settings()
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False

    ssh.send_command(f'ip firewall address-list remove [find address={source_ip} list={DENY_LIST}]')
    ssh.send_command(f'ip firewall address-list add list={PERMANENT_BAN_LIST} address={source_ip} timeout={BAN_TIMEOUT} comment="vpn user"')
    ssh.send_command(f'[/interface l2tp-server remove [find where client-address=[/ppp active get [find where address={source_ip}] value-name=caller-id]]]')
    ssh.disconnect()
    return True


def unban_ip_address(source_ip: str or list) -> bool:
    router = _configure_connection_settings()
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False
    if isinstance(source_ip, list):
        for ip in source_ip:
            ssh.send_command(f'[/ip firewall address-list remove [find address={ip} list={PERMANENT_BAN_LIST}]]')
    else:
        ssh.send_command(f'[/ip firewall address-list remove [find address={source_ip} list={PERMANENT_BAN_LIST}]]')
    ssh.disconnect()
    return True


def disconnect_client(source_ip: str or list) -> bool:
    router = _configure_connection_settings()
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False
    if isinstance(source_ip, list):
        for ip in source_ip:
            cmd = f'[/interface l2tp-server remove [find where client-address=[/ppp active get [find where address={ip}] value-name=caller-id]]]'
            ssh.send_command(cmd)
    else:
        cmd = f'[/interface l2tp-server remove [find where client-address=[/ppp active get [find where address={source_ip}] value-name=caller-id]]]'
        ssh.send_command(cmd)
    ssh.disconnect()
    return True
