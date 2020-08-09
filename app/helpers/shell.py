import os

from netmiko import ConnectHandler, NetmikoTimeoutException


SSH_USERNAME = os.environ.get('SSH_USERNAME')
SSH_PASSWORD = os.environ.get('SSH_PASSWORD')
SSH_PORT = os.environ.get('SSH_PORT')

DENY_LIST = os.environ.get('DENY_LIST')
PERMIT_LIST = os.environ.get('PERMIT_LIST')
PERMANENT_BAN_LIST = os.environ.get('PERMANENT_BAN_LIST')


def _configure_connection_settings(destination_ip: str) -> None:
    router = {
        'device_type': 'mikrotik_routeros',
        'host': destination_ip,
        'username': SSH_USERNAME,
        'password': SSH_PASSWORD,
        'port': SSH_PORT,
        'global_delay_factor': 2,
    }
    return router


def authorize_ip_address(ip_addresses: dict) -> bool:
    source_ip = ip_addresses["source_ip"]
    destination_ip = ip_addresses['destination_ip']

    router = _configure_connection_settings(destination_ip)
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False

    ssh.send_command(f'ip firewall address-list remove [find address={source_ip} list={DENY_LIST}]')
    ssh.send_command(f'ip firewall address-list add list={PERMIT_LIST} address={source_ip}')
    return True


def ban_ip_address(ip_addresses: dict) -> bool:
    source_ip = ip_addresses["source_ip"]
    destination_ip = ip_addresses['destination_ip']
    router = _configure_connection_settings(destination_ip)
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False

    ssh.send_command(f'ip firewall address-list remove [find address={source_ip} list={DENY_LIST}]')
    ssh.send_command(f'ip firewall address-list add list={PERMANENT_BAN_LIST} address={source_ip}')
    ssh.disconnect()
    return True


def disconnect_client(ip_addresses: dict) -> bool:
    source_ip = ip_addresses['source_ip']
    destination_ip = ip_addresses['destination_ip']
    router = _configure_connection_settings(destination_ip)
    try:
        ssh = ConnectHandler(**router)
    except NetmikoTimeoutException:
        return False
    cmd = f'[/interface l2tp-server remove [find where client-address=[/ppp active get [find where address={source_ip}] value-name=caller-id]]]'
    ssh.send_command(cmd)
    ssh.disconnect()
    return True
