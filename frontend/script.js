const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const userText = userInput.value.trim();
  if (!userText) return;

  // Show user message
  appendMessage('User', userText);
  userInput.value = '';

  // Send to backend
  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userText }),
    });

    const data = await res.json();
    appendMessage('FixFlow', data.response);
  } catch (err) {
    appendMessage('FixFlow', '⚠️ Error contacting server.');
  }
});

function appendMessage(sender, message) {
  const msg = document.createElement('div');
  msg.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}



.then(data => {
  // Update response
  document.getElementById("response").innerHTML = data.response;

  // Show summary
  document.getElementById("summary").innerText = "Summary: " + data.summary;

  // Show actions
  let actionsHTML = "<ul>";
  data.actions.forEach(action => {
      actionsHTML += `<li>${action}</li>`;
  });
  actionsHTML += "</ul>";
  document.getElementById("actions").innerHTML = actionsHTML;
});
