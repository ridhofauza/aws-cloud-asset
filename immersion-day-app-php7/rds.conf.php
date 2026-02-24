<?php
/**
 * Copyright 2010-2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * This file is licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License. A copy of
 * the License is located at
 *
 * http://aws.amazon.com/apache2.0/
 *
 * This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
 * CONDITIONS OF ANY KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations under the License.
 *
 * If you need more information about configurations or implementing the sample code, visit the AWS docs:
 * https://aws.amazon.com/developers/getting-started/php/
 *
 */
  $ch = curl_init();

  // get a valid TOKEN
  $headers = array (
        'X-aws-ec2-metadata-token-ttl-seconds: 60' );
  $url = "http://169.254.169.254/latest/api/token";

  curl_setopt( $ch, CURLOPT_URL, $url );
  curl_setopt( $ch, CURLOPT_HTTPHEADER, $headers );
  curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
  curl_setopt( $ch, CURLOPT_CUSTOMREQUEST, "PUT" );
  curl_setopt( $ch, CURLOPT_URL, $url );
  $token = curl_exec( $ch );

require 'vendor/aws-autoloader.php';

use Aws\SecretsManager\SecretsManagerClient; 
use Aws\Exception\AwsException;

// Name of secret containing the database connection information
$secretName = 'mysecret';

  $headers = array (
        'X-aws-ec2-metadata-token: '.$token );
  $url="http://169.254.169.254/latest/dynamic/instance-identity/document";

  curl_setopt( $ch, CURLOPT_URL, $url );
  curl_setopt( $ch, CURLOPT_HTTPHEADER, $headers );
  curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
  curl_setopt( $ch, CURLOPT_CUSTOMREQUEST, "GET" );
  $urlDocument = curl_exec( $ch );

// Link local data provides information bout this instance  
// $urlDocument = "http://169.254.169.254/latest/dynamic/instance-identity/document";
// $document = file_get_contents($urlDocument);
$data = json_decode($urlDocument, true);
$region = $data['region'];

/**
 * In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
 * See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
 * We rethrow the exception by default.
 *
 * This code expects that you have AWS credentials set up per:
 * https://docs.aws.amazon.com/sdk-for-php/v3/developer-guide/guide_credentials.html
 */

// Create a Secrets Manager Client 
$client = new SecretsManagerClient([
    'version' => '2017-10-17',
    'region' => $region,
]);


try {
    $result = $client->getSecretValue([
        'SecretId' => $secretName,
    ]);

} catch (AwsException $e) {
    $error = $e->getAwsErrorCode();
    echo "Error: ".$error."<br/>";
    die("");
}
//
// Decrypts secret using the associated KMS CMK.
// Depending on whether the secret is a string or binary, one of these fields will be populated.
if (!isset($result['SecretString'])) {
    echo "Error: Unable to retrieve secret";
    die("");
}

$secret = json_decode($result['SecretString'], true);

// Provide values for DB connection
$RDS_URL=$secret['host'];
$RDS_DB=$secret['dbname'];
$RDS_user=$secret['username'];
$RDS_pwd=$secret['password'];
 
?>