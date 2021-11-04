
// Send delete request message <id>
function DeleteMessage(id) {
    var xhttp = new XMLHttpRequest()
    xhttp.open("DELETE", "/message/" + id, true)
    xhttp.send()
    window.location.href = "/mailbox"
}

// Enable edit on readonly text
function toggleEdit() {
  document.getElementById('firstname').readOnly = false
  document.getElementById('lastname').readOnly = false
  document.getElementById('email').readOnly = false
  document.getElementById('location').readOnly = false
}
