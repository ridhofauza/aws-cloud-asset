<?php
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

  echo "<table>";
  echo "<tr><th>Meta-Data</th><th>Value</th></tr>";

  #The URL root is the AWS meta data service URL where metadata
  # requests regarding the running instance can be made
  # $urlRoot="http://169.254.169.254/latest/meta-data/";

  # Get the instance ID from meta-data and print to the screen
  $headers = array (
        'X-aws-ec2-metadata-token: '.$token );
  $url="http://169.254.169.254/latest/meta-data/";

  curl_setopt( $ch, CURLOPT_URL, $url . 'instance-id' );
  curl_setopt( $ch, CURLOPT_HTTPHEADER, $headers );
  curl_setopt( $ch, CURLOPT_RETURNTRANSFER, true );
  curl_setopt( $ch, CURLOPT_CUSTOMREQUEST, "GET" );
  $result = curl_exec( $ch );

  echo "<tr><td>InstanceId</td><td><i>" . $result . "</i></td><tr>";

  # Availability Zone
  curl_setopt( $ch, CURLOPT_URL, $url . 'placement/availability-zone' );
  $result2 = curl_exec( $ch );

  echo "<tr><td>Availability Zone</td><td><i>" . $result2 . "</i></td><tr>";

  echo "</table>";

?>