import { X, ShieldCheck, SearchCheck, CheckCircle2 } from "lucide-react";

function AboutModal({ isOpen, onClose }) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
            <div className="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl border border-slate-100">
                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="cursor-pointer absolute top-4 right-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
                    aria-label="Tutup"
                >
                    <X size={18} />
                </button>

                {/* Header Logo & Title */}
                <div className="flex items-center gap-3 mb-4">
                    {/* <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm"> */}
                    <img
                        src="/Coat_of_arms_of_Aceh.svg"
                        alt="Logo Aceh"
                        className="h-9 w-auto object-contain"
                    />
                    {/* </div> */}
                    <div>
                        <h3 className="text-base font-bold text-slate-900">
                            TUPOKSI AI
                        </h3>
                        <p className="text-xs text-slate-500">Asisten Informasi Regulasi & SOTK</p>
                    </div>
                </div>

                {/* Description */}
                <p className="text-xs leading-relaxed text-slate-600 mb-5">
                    Layanan asisten cerdas yang dirancang untuk membantu pegawai dan masyarakat dalam mencari informasi mengenai Kedudukan, Susunan Organisasi, Tugas, Fungsi, dan Tata Kerja di lingkungan Dinas Komunikasi, Informatika dan Persandian Aceh.
                </p>

                {/* Features List */}
                <div className="space-y-3 mb-6">
                    <div className="flex items-start gap-2.5 text-xs text-slate-700">
                        <ShieldCheck size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                        <span><strong>Basis Regulasi Sah:</strong> Merujuk pada Pergub Aceh No. 119/2016 dan Pergub Aceh No. 61/2020.</span>
                    </div>

                    <div className="flex items-start gap-2.5 text-xs text-slate-700">
                        <SearchCheck size={16} className="text-blue-600 shrink-0 mt-0.5" />
                        <span><strong>Pemetaan Tugas:</strong> Menghubungkan seluruh struktur dinas, bidang, hingga UPTD langsung dengan pasal dan ayat yang sesuai.</span>
                    </div>

                    <div className="flex items-start gap-2.5 text-xs text-slate-700">
                        <CheckCircle2 size={16} className="text-purple-600 shrink-0 mt-0.5" />
                        <span><strong>Rujukan Sumber Resmi:</strong> Setiap jawaban dilengkapi rujukan pasal dan halaman naskah asli agar mudah diverifikasi.</span>
                    </div>
                </div>

                {/* Footer Info */}
                <div className="border-t border-slate-100 pt-4 flex items-center justify-between text-[11px] text-slate-400">
                    <span>Versi Sistem v1.2.0</span>
                    <span>© Diskominsa Aceh</span>
                </div>
            </div>
        </div >
    );
}

export default AboutModal;