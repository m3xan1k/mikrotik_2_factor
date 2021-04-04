
# on up

{
    :local name ($"user");
	:local sourceIp ($"remote-address");
    :local destinationIp ($"local-address");
    :local denyList "sandboxed";
    :local callerId ($"caller-id");
    
    :log info $sourceIp;
    :log info $destinationIp;
    :log info $denyList;
    
    :local chatId [/ppp secret get [find name=$user] comment];
    :local endpointUrl "http://192.168.88.254/clients/connect/"
    
    :local payload "{\"name\": \"$name\", \"chat_id\": \"$chatId\", \"source_ip\": \"$sourceIp\", \"destination_ip\": \"$destinationIp\", \"caller_id\": \"$callerId\"}";
    
    [/ip firewall address-list add list=$denyList address=$sourceIp comment="vpn user"];
    
    [/tool fetch url=$endpointUrl http-header-field="content-type:application/json" http-method=post http-data=$payload];
    
}

# on down

{

	:local sourceIp ($"remote-address");
    :local destinationIp ($"local-address");
    :local denyList "sandboxed";
    :local permitList "allowed";
    :local chatId [/ppp secret get [find name=$user] comment];
    :local endpointUrl "http://192.168.88.254/clients/disconnect/"
    
    :local payload "{\"chat_id\": \"$chatId\", \"source_ip\": \"$sourceIp\", \"destination_ip\": \"$destinationIp\", \"caller_id\": \"$callerId\"}";
    
    [ip firewall address-list remove [find address=$sourceIp list=$permitList]];
    
    [ip firewall address-list remove [find address=$sourceIp list=$denyList]];

    [/tool fetch url=$endpointUrl http-header-field="content-type:application/json" http-method=post http-data=$payload];
    
}
