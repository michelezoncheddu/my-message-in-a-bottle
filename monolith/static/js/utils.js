
// Send delete request message <id>
function DeleteMessage(id) {
    fetch('/message/' + id, {
        method: 'DELETE'
    }).then(_ => window.location.href = '/mailbox')
}

// Enable edit on readonly text
function toggleEdit() {
    document.getElementById('firstname').readOnly = false
    document.getElementById('lastname').readOnly = false
    document.getElementById('email').readOnly = false
    document.getElementById('location').readOnly = false
}
