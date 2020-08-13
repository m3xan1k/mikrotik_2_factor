
# on up

{
	:local sourceIp ($"remote-address");
    :local destinationIp ($"local-address");
    :local denyList "sandboxed";
    
    :log info $sourceIp;
    :log info $destinationIp;
    :log info $denyList;
    
    :local chatId [/ppp secret get [find name=$user] comment];
    :local endpointUrl "http://192.168.90.6/clients/connect/"
    
    :local payload "{\"chat_id\": \"$chatId\", \"source_ip\": \"$sourceIp\", \"destination_ip\": \"$destinationIp\"}";
    
    [/ip firewall address-list add list=$denyList address=$sourceIp comment="vpn user"];
    
    [/tool fetch url=$endpointUrl http-header-field="content-type:application/json" http-method=post http-data=$payload];
    
}

# on down

{
	:local sourceIp ($"remote-address");
    :local destinationIp ($"local-address");
    :local denyList "sandboxed";
    
    :log info $sourceIp;
    :log info $destinationIp;
    :log info $denyList;
    
    :local chatId [/ppp secret get [find name=$user] comment];
    :local endpointUrl "http://192.168.90.6/clients/connect/"
    
    :local payload "{\"chat_id\": \"$chatId\", \"source_ip\": \"$sourceIp\", \"destination_ip\": \"$destinationIp\"}";
    
    [/ip firewall address-list add list=$denyList address=$sourceIp];
    
    [/tool fetch url=$endpointUrl http-header-field="content-type:application/json" http-method=post http-data=$payload];
    
}
