
// Send delete request message <id>
function DeleteMessage(id) {
    var xhttp = new XMLHttpRequest()
    xhttp.open("DELETE", "/message/" + id, true)
    xhttp.send()
}

function test2() {
  document.getElementById('test').removeAttribute('readonly');
}