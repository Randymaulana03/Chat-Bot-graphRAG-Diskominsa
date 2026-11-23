import { ShieldCheck, Building2, Cpu, Network } from "lucide-react";

function EmptyState({ onSelectPrompt }) {
    const prompts = [
        {
            title: "Apa tugas UPTD Statistik",
            desc: "Pergub Aceh No. 61 Tahun 2020",
            icon: ShieldCheck,
            query: "Apa tugas UPTD Statistik",
        },
        {
            title: "Tugas & Fungsi Diskominsa",
            desc: "Kedudukan & Tupoksi Kelembagaan",
            icon: Building2,
            query: "Apa tugas dan fungsi Dinas Komunikasi, Informatika dan Persandian Aceh",
        },
        {
            title: "Apa tugas Bidang TIK",
            desc: "Layanan Infrastruktur & E-Gov",
            icon: Cpu,
            query: "Apa tugas Bidang TIK",
        },
        {
            title: "Struktur Organisasi Diskominsa",
            desc: "Bagan Hirarki & Pembagian Kerja",
            icon: Network,
            query: "Bagaimana struktur organisasi Diskominsa",
        },
    ];

    return (
        <div className="mx-auto flex max-w-2xl flex-col items-center justify-center py-10 text-center">
            <div className="mb-4">
                <img
                    src="Coat_of_arms_of_Aceh.svg"
                    alt="Coat of Arms of Aceh"
                    className="w-20 h-auto"
                />
            </div>

            <h2 className="text-xl font-bold text-slate-900">
                Selamat datang di TUPOKSI AI - Diskominsa
            </h2>
            <p className="mt-1 text-sm text-slate-500">
                Fokus membantu menjawab pertanyaan seputar Tugas Pokok dan Fungsi internal.
            </p>

            <div className="mt-8 grid w-full grid-cols-1 gap-3 sm:grid-cols-2">
                {prompts.map((item, idx) => {
                    const Icon = item.icon;
                    return (
                        <button
                            key={idx}
                            onClick={() => onSelectPrompt(item.query)}
                            className="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition-all hover:border-slate-300 hover:shadow-md"
                        >
                            <div className="rounded-lg bg-slate-50 p-2 text-slate-700">
                                <Icon size={18} />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-slate-800">{item.title}</p>
                                <p className="text-xs text-slate-400">{item.desc}</p>
                            </div>
                        </button>
                    );
                })}
            </div>
        </div>
    );
}

export default EmptyState;