<?php 
  
// Complex array 
$myvar = [
    "total_payments_paid_amount" => 249.4
]; 
  
// Convert to a string 
$string = serialize($myvar); 
  
// Printing the serialized data 
echo $string; 