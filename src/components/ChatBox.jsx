import React from "react"
import MessageBubble from "./MessageBubble"
import InputBar from "./InputBar"

function ChatBox({ messages, onSend }) {
  return (
    <div>
      {messages.map((msg, i) => (
        <MessageBubble key={i} text={msg.text} sender={msg.sender} />
      ))}
      <InputBar onSend={onSend} />
    </div>
  )
}

export default ChatBox
