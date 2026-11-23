import { useState, useEffect, useRef } from "react";
import Sidebar from "./components/Sidebar";
import ChatHeader from "./components/ChatHeader";
import ChatInput from "./components/ChatInput";
import ChatMessage from "./components/ChatMessage";
import EmptyState from "./components/EmptyState";
import { ArrowDown } from "lucide-react";
import { getRandomTaskHints } from "./data/taskHints";
import ThinkingIndicator from "./components/ThinkingIndicator";

const STORAGE_KEY_CHATS = "diskominsa_chat_history";
const STORAGE_KEY_CACHE = "diskominsa_api_cache";

function App() {
  const [initialNewChatId] = useState(() => Date.now().toString());

  const [chats, setChats] = useState(() => {
    const saved = localStorage.getItem(STORAGE_KEY_CHATS);
    let existingChats = [];
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        existingChats = parsed.filter((c) => c.messages && c.messages.length > 0);
      } catch (e) {
        console.error(e);
      }
    }
    const newChat = {
      id: initialNewChatId,
      title: "Obrolan Baru",
      messages: [],
    };
    return [newChat, ...existingChats];
  });

  const [activeChatId, setActiveChatId] = useState(initialNewChatId);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [loadingChatId, setLoadingChatId] = useState(null); // <-- Sudah dipindahkan ke dalam fungsi App
  const [currentHints, setCurrentHints] = useState([]);
  const [showScrollButton, setShowScrollButton] = useState(false);

  const mainScrollRef = useRef(null);
  const messagesEndRef = useRef(null);

  const activeChat = chats.find((c) => c.id === activeChatId) || chats[0];

  useEffect(() => {
    const validChats = chats.filter((c) => c.messages && c.messages.length > 0);
    localStorage.setItem(STORAGE_KEY_CHATS, JSON.stringify(validChats));
  }, [chats]);

  // Helper scroll yang mulus dan presisi
  const scrollToBottom = (behavior = "smooth") => {
    const container = mainScrollRef.current;
    if (!container) return;

    if (behavior === "auto") {
      container.scrollTop = container.scrollHeight;
      return;
    }

    const startPosition = container.scrollTop;
    const targetPosition = container.scrollHeight - container.clientHeight;
    const distance = targetPosition - startPosition;

    if (Math.abs(distance) < 5) return;

    const duration = 350;
    let startTime = null;

    const easeOutCubic = (t) => 1 - Math.pow(1 - t, 3);

    const animationStep = (currentTime) => {
      if (!startTime) startTime = currentTime;
      const timeElapsed = currentTime - startTime;
      const progress = Math.min(timeElapsed / duration, 1);

      container.scrollTop = startPosition + distance * easeOutCubic(progress);

      if (progress < 1) {
        requestAnimationFrame(animationStep);
      }
    };

    requestAnimationFrame(animationStep);
  };

  useEffect(() => {
    scrollToBottom("auto");
  }, [activeChatId, activeChat.messages.length, isLoading]);

  const handleScroll = () => {
    if (!mainScrollRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = mainScrollRef.current;
    setShowScrollButton(scrollHeight - scrollTop - clientHeight > 150);
  };

  const handleSelectChat = (id) => {
    setActiveChatId(id);
    setSidebarOpen(false);
    setInput(""); // Reset input saat berpindah obrolan

    const targetChat = chats.find((c) => c.id === id);

    if (targetChat && targetChat.messages.length > 0) {
      const lastMsg = targetChat.messages[targetChat.messages.length - 1];

      if (lastMsg.hints && lastMsg.hints.length > 0) {
        setCurrentHints(lastMsg.hints);
      } else {
        setCurrentHints(getRandomTaskHints(2));
      }
    } else {
      setCurrentHints([]);
    }
  };

  const handleNewChat = () => {
    if (activeChat && activeChat.messages.length === 0) {
      setSidebarOpen(false);
      return;
    }

    const newId = Date.now().toString();
    const newChat = { id: newId, title: "Obrolan Baru", messages: [] };
    setChats((prevChats) => [newChat, ...prevChats]);
    setActiveChatId(newId);
    setSidebarOpen(false);
    setCurrentHints([]);
  };

  const handleDeleteChat = (id) => {
    const filtered = chats.filter((c) => c.id !== id);
    if (filtered.length === 0) {
      const resetChat = [{ id: Date.now().toString(), title: "Obrolan Baru", messages: [] }];
      setChats(resetChat);
      setActiveChatId(resetChat[0].id);
    } else {
      setChats(filtered);
      if (activeChatId === id) setActiveChatId(filtered[0]?.id || "");
    }
  };

  const normalizeQuery = (str) => str.trim().toLowerCase().replace(/\s+/g, " ");

  const handleSendMessage = async (customQuery) => {
    const query = customQuery || input;
    if (!query.trim() || isLoading) return;

    setCurrentHints([]);
    const normalizedKey = normalizeQuery(query);
    const userMessage = { role: "user", content: query };
    const currentChatId = activeChatId;

    // Catat ID chat yang sedang melakukan loading
    setIsLoading(true);
    setLoadingChatId(currentChatId);

    // 🔄 RE-ORDER LOGIC: Tambah pesan user DENGAN memindahkan chat aktif ke urutan paling atas [0]
    setChats((prevChats) => {
      const targetChat = prevChats.find((c) => c.id === currentChatId);
      if (!targetChat) return prevChats;

      const isFirst = targetChat.messages.length === 0;
      const updatedChat = {
        ...targetChat,
        title: isFirst ? query.slice(0, 24) + "..." : targetChat.title,
        messages: [...targetChat.messages, userMessage],
      };

      const otherChats = prevChats.filter((c) => c.id !== currentChatId);

      // Kembalikan array baru: chat aktif di urutan [0], sisa chat di bawahnya
      return [updatedChat, ...otherChats];
    });

    setInput("");
    const newHints = getRandomTaskHints(2);

    const savedCache = localStorage.getItem(STORAGE_KEY_CACHE);
    let apiCache = savedCache ? JSON.parse(savedCache) : {};

    // 1. Handling Jika Jawaban Ada di Cache
    if (apiCache[normalizedKey]) {
      console.log("⚡ [Cache Hit] Mengambil jawaban dari localStorage untuk query:", normalizedKey);
      const cachedData = apiCache[normalizedKey];
      const botMessage = {
        role: "assistant",
        content: cachedData.answer,
        sources: cachedData.sources || [],
        hints: newHints,
      };

      // Update pesan bot (posisi chat aktif sudah pasti ada di paling atas [0])
      setChats((prevChats) =>
        prevChats.map((c) =>
          c.id === currentChatId
            ? { ...c, messages: [...c.messages, botMessage] }
            : c
        )
      );

      setCurrentHints(newHints);
      setIsLoading(false);
      setLoadingChatId(null);
      return;
    }

    // 2. Handling Request API Backend
    try {
      const res = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: query }),
      });

      if (!res.ok) throw new Error("Gagal mengambil data dari server");

      const data = await res.json();

      const botMessage = {
        role: "assistant",
        content: data.answer,
        sources: data.sources || [],
        hints: newHints,
      };

      apiCache[normalizedKey] = {
        answer: data.answer,
        sources: data.sources || [],
      };
      localStorage.setItem(STORAGE_KEY_CACHE, JSON.stringify(apiCache));

      setChats((prevChats) =>
        prevChats.map((c) =>
          c.id === currentChatId
            ? { ...c, messages: [...c.messages, botMessage] }
            : c
        )
      );

      setCurrentHints(newHints);
    } catch (err) {
      console.error(err);
      const errorMessage = {
        role: "assistant",
        content: "Mohon maaf, terjadi kesalahan saat menghubungkan ke server.",
        sources: [],
        hints: newHints,
      };

      setChats((prevChats) =>
        prevChats.map((c) =>
          c.id === currentChatId
            ? { ...c, messages: [...c.messages, errorMessage] }
            : c
        )
      );

      setCurrentHints(newHints);
    } finally {
      setIsLoading(false);
      setLoadingChatId(null);
    }
  };

  return (
    <div className="flex h-screen bg-white font-sans text-slate-800 antialiased">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />

      <div className="relative flex flex-1 flex-col overflow-hidden">
        <ChatHeader
          onToggleSidebar={() => setSidebarOpen(true)}
          onNewChat={handleNewChat}
        />

        <main
          ref={mainScrollRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto p-4 sm:p-6"
        >
          <div className="mx-auto max-w-4xl space-y-6">
            {/* Isi Pesan */}
            {activeChat.messages.length === 0 ? (
              <EmptyState onSelectPrompt={(q) => handleSendMessage(q)} />
            ) : (
              activeChat.messages.map((msg, idx) => (
                <ChatMessage
                  key={idx}
                  role={msg.role}
                  content={msg.content}
                  sources={msg.sources}
                />
              ))
            )}

            {isLoading && loadingChatId === activeChatId && <ThinkingIndicator />}
            {/* Target scroll paling bawah */}
            <div ref={messagesEndRef} />
          </div>
        </main>

        {showScrollButton && (
          <div className="pointer-events-none absolute bottom-34 inset-x-0 z-20 flex justify-center animate-in fade-in slide-in-from-bottom-3 duration-300">
            <button
              type="button"
              onClick={() => scrollToBottom("smooth")}
              className="pointer-events-auto cursor-pointer flex items-center gap-2 rounded-full border border-slate-200/80 bg-white/90 px-4 py-2 text-xs font-semibold text-slate-700 shadow-md backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5 hover:bg-white hover:text-slate-900 hover:shadow-xl active:translate-y-0 active:scale-95 animate-bounce-subtle"
            >
              <ArrowDown size={16} className="text-slate-800 transition-transform duration-300 group-hover:translate-y-0.5" />
              <span>Ke pesan terbaru</span>
            </button>
          </div>
        )}

        <footer className="border-t border-slate-100 bg-white p-4">
          <div className="mx-auto max-w-3xl">
            {!isLoading && currentHints.length > 0 && (
              <div className="mb-3 flex flex-wrap items-center gap-2">
                <span className="text-xs font-medium text-slate-400">
                  Rekomendasi pertanyaan:
                </span>
                {currentHints.map((hint, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSendMessage(hint)}
                    className="cursor-pointer rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs text-slate-600 transition hover:border-slate-300 hover:bg-slate-100 hover:text-slate-900 active:scale-95"
                  >
                    💡 {hint}
                  </button>
                ))}
              </div>
            )}

            <ChatInput
              value={input}
              onChange={setInput}
              onSubmit={() => handleSendMessage()}
              disabled={isLoading}
            />
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;