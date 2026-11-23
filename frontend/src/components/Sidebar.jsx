import { useState } from "react";
import { Plus, MessageSquare, Trash2, X, Info } from "lucide-react";
import AboutModal from "./AboutModal";

function Sidebar({ isOpen, onClose, chats, activeChatId, onSelectChat, onNewChat, onDeleteChat }) {
    const [isAboutOpen, setIsAboutOpen] = useState(false);

    return (
        <>
            {/* Overlay Mobile */}
            {isOpen && (
                <div
                    onClick={onClose}
                    className="fixed inset-0 z-20 bg-slate-900/40 backdrop-blur-sm md:hidden"
                />
            )}

            <aside
                className={`fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-slate-200 bg-slate-50 transition-transform duration-200 ease-in-out md:static md:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"
                    }`}
            >
                {/* Header Sidebar (Tombol Obrolan Baru) */}
                <div className="flex items-center justify-between border-b border-slate-200 p-4">
                    <button
                        onClick={onNewChat}
                        className="cursor-pointer flex flex-1 items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800 active:scale-95"
                    >
                        <Plus size={18} />
                        Obrolan Baru
                    </button>

                    <button
                        onClick={onClose}
                        className="cursor-pointer ml-2 rounded-lg p-2 text-slate-500 hover:bg-slate-200 md:hidden"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* List History Obrolan */}
                {/* List History Obrolan */}
                <div className="flex-1 overflow-y-auto p-3">
                    <p className="mb-2 px-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                        Riwayat Obrolan
                    </p>

                    {/* Tambahkan transition-all duration-300 ease-in-out */}
                    <div className="space-y-1 transition-all duration-300 ease-in-out">
                        {chats
                            .filter((chat) => chat.messages && chat.messages.length > 0)
                            .map((chat) => (
                                <div
                                    key={chat.id}
                                    className={`group flex items-center justify-between rounded-xl px-3 py-2.5 text-sm transition-all duration-300 ease-in-out ${activeChatId === chat.id
                                            ? "bg-white font-medium text-slate-900 shadow-sm border border-slate-200 animate-in fade-in slide-in-from-top-2 duration-300"
                                            : "text-slate-600 hover:bg-slate-200/60"
                                        }`}
                                >
                                    <button
                                        type="button"
                                        onClick={() => onSelectChat(chat.id)}
                                        className="cursor-pointer flex flex-1 items-center gap-2.5 truncate text-left"
                                    >
                                        <MessageSquare size={16} className="shrink-0 text-slate-400" />
                                        <span className="truncate">{chat.title}</span>
                                    </button>

                                    {chats.length > 1 && (
                                        <button
                                            type="button"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                onDeleteChat(chat.id);
                                            }}
                                            className="cursor-pointer opacity-0 transition group-hover:opacity-100 p-1 text-slate-400 hover:text-red-500"
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    )}
                                </div>
                            ))}
                    </div>
                </div>

                {/* BOTTOM FOOTER: Tombol Tentang Aplikasi */}
                <div className="border-t border-slate-200 p-3">
                    <button
                        onClick={() => setIsAboutOpen(true)}
                        className="cursor-pointer flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-200/60 hover:text-slate-900"
                    >
                        <Info size={17} className="text-slate-500" />
                        <span>Tentang Aplikasi</span>
                    </button>
                </div>
            </aside>

            {/* Modal Dialog Info */}
            <AboutModal isOpen={isAboutOpen} onClose={() => setIsAboutOpen(false)} />
        </>
    );
}

export default Sidebar;