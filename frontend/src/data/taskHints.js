export const TASK_HINTS_POOL = [
  "Apa tugas Seksi Infrastruktur dan Teknologi?",
  "Apa tugas Seksi Pengelolaan Data dan Integrasi Sistem Informasi?",
  "Apa tugas Seksi Keamanan Informasi E-Government?",
  "Apa tugas Seksi Tata Kelola Persandian?",
  "Apa tugas Seksi Operasional Pengamanan Persandian?",
  "Apa tugas Bidang Layanan E-Government?",
  "Apa tugas Bidang Pengelolaan Komunikasi Publik?",
  "Apa tugas Sekretariat Diskominsa Aceh?",
  "Apa tugas Kepala UPTD Statistik?",
];

export const getRandomTaskHints = (count = 2) => {
  const shuffled = [...TASK_HINTS_POOL].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};