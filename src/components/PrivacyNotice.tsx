import { LockKeyhole, Database, Eye } from 'lucide-react'

export default function PrivacyNotice() {
  return <section id="privacy" className="py-20 px-6 bg-[#0d1424] scroll-mt-6">
    <div className="max-w-5xl mx-auto glass-card rounded-3xl p-7 md:p-10">
      <span className="text-xs font-semibold text-emerald-300 uppercase tracking-widest">Privacy and data notice</span>
      <h2 className="mt-3 text-3xl md:text-4xl font-black text-white">Clear about what this student project stores.</h2>
      <div className="mt-8 grid md:grid-cols-3 gap-5">
        <div className="rounded-2xl bg-white/[0.03] p-5"><LockKeyhole className="w-5 h-5 text-sky-300" /><h3 className="mt-3 font-bold text-white">Account data</h3><p className="mt-2 text-sm leading-relaxed text-slate-400">Your email, display name, password hash, session records, saved destinations, and trip plans are stored only to operate your account.</p></div>
        <div className="rounded-2xl bg-white/[0.03] p-5"><Database className="w-5 h-5 text-indigo-300" /><h3 className="mt-3 font-bold text-white">Place data</h3><p className="mt-2 text-sm leading-relaxed text-slate-400">The catalogue is sourced from GeoNames under CC BY 4.0. Travel photos are representative Unsplash images, not a claim that a picture depicts each city.</p></div>
        <div className="rounded-2xl bg-white/[0.03] p-5"><Eye className="w-5 h-5 text-purple-300" /><h3 className="mt-3 font-bold text-white">Your control</h3><p className="mt-2 text-sm leading-relaxed text-slate-400">Do not enter travel documents or payment information. This project does not process bookings or provide live safety advice.</p></div>
      </div>
      <p className="mt-6 text-xs leading-relaxed text-slate-500">This is an educational project disclosure, not a lawyer-reviewed commercial privacy policy.</p>
    </div>
  </section>
}
