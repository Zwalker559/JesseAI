import React from "react"

function MessageBubble({ text, sender }) {
  return (
    <div style={{ textAlign: sender === "user" ? "right" : "left" }}>
      <p>{text}</p>
    </div>
  )
}

export default MessageBubble
