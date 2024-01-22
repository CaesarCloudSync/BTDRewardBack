<?php

$ch = curl_init();
// CONNECT TO API, VERIFY MY API KEY AND PASSWORD AND GET THE LEAD DATA
curl_setopt($ch, CURLOPT_URL,"https://app.kartra.com/api");
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS,
    http_build_query(
        array(
            'app_id' => 'eEQfVDqnzWbJ',
            'api_key' => 'fPvimQSo',
            'api_password' => 'xfdgUTCcYEqD',
            'lead' => array(
                'email' => 'testkartra@gmail.com',
                'first_name' => 'Test',
                'last_name' => 'Kartra',           
                'custom_fields' => [
                    '0' => [
                               'field_identifier' => 'text1',
                               'field_value' => 'text message'
                           ],
                    '1' => [
                               'field_identifier' => 'dropdown1',
                               'field_value' => '612'
                           ],
                    '2' => [
                               'field_identifier' => 'checkbox1',
                               'field_value' => ['620', '621']
                           ],
                ]  // Please read Note (1) below 
            ),
            'actions' => array(
                '0' => array(
                       'cmd' => 'create_lead',
                ),
                '1' => array(
                       'cmd' => 'assign_tag',
                       'tag_name' => 'Membership2024 - GBP 30 Trial'
                )
            )
      )
   )
);

// REQUEST CONFIRMATION MESSAGE FROM API…
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$server_output = curl_exec ($ch);
curl_close ($ch);
$server_json = json_decode($server_output);
print_r($server_json);
switch ($server_json->status) {
    case "Error" :
        // process what error was about
        break;
    case "Success" :
        // after this you can use the info passed from kartra in your own scripts. 
        // Ex: $server_json->lead_details contains the lead details
        break;
}

?>