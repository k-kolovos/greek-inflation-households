"""Πληθωρισμός ανά πεμπτημόριο νοικοκυριών, Σεπτέμβριος 2026.
Σταθμισμένος μέσος των ετήσιων μεταβολών των 13 ομάδων του ΔΤΚ με τα μερίδια δαπάνης της ΕΟΠ 2025."""
import csv
sh=list(csv.DictReader(open('eop2025_pinakas15_pemptimoria.csv',encoding='utf-8')))
r=[float(x['etisia_metavoli_pct']) for x in csv.DictReader(open('dtk_sept2026_etisia_metavoli.csv',encoding='utf-8'))][:13]
for q in ['q1','q2','q3','q4','q5']:
    w=[float(x[q]) for x in sh]; s=sum(w)
    c=[wi*ri/s for wi,ri in zip(w,r)]
    print(q, 'πληθωρισμός %.2f%%' % sum(c), '| στέγαση %.2f μον.' % c[3], '| μεταφορές %.2f μον.' % c[6])
