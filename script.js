async function sendMessage() {
  const input = document.getElementById('user-input').value;
  const chatBox = document.getElementById('chat-box');

  const response = await fetch('/.netlify/functions/chatbot', {
    method: 'POST',
    body: JSON.stringify({ message: input }),
  });

  const data = await response.json();
  chatBox.innerHTML += `<p><strong>You:</strong> ${input}</p><p><strong>Bot:</strong> ${data.reply}</p>`;
  document.getElementById('user-input').value = '';
}
