/*Script Handler*/
class helperMethod {
   static createAlert(p_header_key, p_message_key, p_header, p_message, p_confirm_key, isConfirmation, p_cancel_confirm_key , p_confirm_function) {
    document.getElementById(p_header_key).innerHTML = p_header
    document.getElementById(p_message_key).innerHTML = p_message
    document.getElementById(p_confirm_key).onclick = p_confirm_function
    if(isConfirmation) {
       document.getElementById(p_cancel_confirm_key).style.visibility = 'visible';
    } else {
       document.getElementById(p_cancel_confirm_key).style.visibility = 'hidden';
    }

    $("#myModal").modal();
  }
}
