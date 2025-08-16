import React, { useState } from "react"

function InputBar({ onSend }) {
  const [input, setInput] = useState("")

  const handleSend = () => {
    if (input.trim()) {
      onSend(input)
      setInput("")
    }
  }

  return (
    <div>
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={handleSend}>Send</button>
    </div>
  )
}

export default InputBar
