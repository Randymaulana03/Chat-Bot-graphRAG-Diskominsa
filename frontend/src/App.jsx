import { useState } from "react"
const API_URL = import.meta.env.VITE_API_URL
import ChatHeader from "./components/ChatHeader"
import ChatMessage from "./components/ChatMessage"
import ChatInput from "./components/ChatInput"

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      content: "Halo! Ada yang bisa saya bantu?",
      sources: [],
    },
  ])

  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    const question = input.trim()

    if (!question || loading) {
      return
    }

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: question,
      sources: [],
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      userMessage,
    ])

    setInput("")
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
        }),
      })

      if (!response.ok) {
        throw new Error("Gagal menghubungi server")
      }

      const data = await response.json()

      const assistantMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        assistantMessage,
      ])
    } catch (error) {
      console.error(error)

      const errorMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content:
          "Maaf, terjadi kesalahan saat menghubungi server.",
        sources: [],
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        errorMessage,
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    // 1. Kunci layar setinggi 100vh dan matikan scroll penuh halaman (overflow-hidden)
    <div className="flex h-screen flex-col overflow-hidden bg-slate-50">
      <ChatHeader />

      {/* 2. Container pesan (Scrollable) */}
      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col overflow-y-auto px-6 py-6">
        <div className="space-y-4">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
              sources={message.sources}
            />
          ))}

          {loading && (
            <ChatMessage
              role="assistant"
              content="Sedang mencari informasi..."
              sources={[]}
            />
          )}
        </div>
      </main>

      {/* 3. Area Input (Fixed & Terkunci di Bawah) */}
      <div className="border-t border-slate-200/60 bg-white/80 p-4 backdrop-blur-md">
        <div className="mx-auto max-w-5xl">
          <ChatInput
            value={input}
            onChange={setInput}
            onSubmit={handleSend}
            disabled={loading}
          />
        </div>
      </div>
    </div>
  )
}

export default App