import React, { useState } from "react"
import ChatBox from "../components/ChatBox"

function Home() {
  const [messages, setMessages] = useState([])

  const handleSend = async (text) => {
    setMessages(prev => [...prev, { text, sender: "user" }])
    const res = await fetch("/.netlify/functions/chat", {
      method: "POST",
      body: JSON.stringify({ message: text })
    })
    const data = await res.json()
    setMessages(prev => [...prev, { text: data.reply, sender: "bot" }])
  }

  return <ChatBox messages={messages} onSend={handleSend} />
}

export default Home
