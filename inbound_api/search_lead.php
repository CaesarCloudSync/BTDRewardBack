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
                'email' => 'maintestkartra@kartra.com',     
            ),
            'actions' => array(
                '0' => array(
                       'cmd' => 'search_lead',
                 ),
            )
      )
   )
);

// REQUEST CONFIRMATION MESSAGE FROM API…
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$server_output = curl_exec ($ch);
curl_close ($ch);
$server_json = json_decode($server_output);
print_r($server_json)



?>