
import numpy as np
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

# 1. الاتصال بالمعالج
service = QiskitRuntimeService(channel="ibm_quantum_platform", token="........")
backend = service.backend("ibm_torino")

# 2. إعداد المسح الزاوي (من -0.1 إلى 0.1 راديان)
# هذا المجال هو "منطقة المناورة" التي تختبئ فيها تصحيحات IBM
angles = np.linspace(-0.1, 0.1, 15)
circuits = []

for theta in angles:
    qc = QuantumCircuit(1, 1)
    # بناء دارة اختبار حساسة جداً للانزياح
    qc.h(0)
    for _ in range(100): # عمق ثابت للمقارنة
        qc.id(0)
    qc.rz(theta, 0) # حقن زاوية اختبار
    qc.h(0)
    qc.measure(0, 0)
    circuits.append(transpile(qc, backend))

# 3. التشغيل
sampler = SamplerV2(mode=backend)
job = sampler.run(circuits)
print(f"🔎 جاري استنطاق المعالج... Job ID: {job.job_id()}")

# 4. تحليل "بصمة التصحيح"
result = job.result()
fidelities = []
for i in range(len(angles)):
    counts = result[i].data.c.get_counts()
    fidelities.append((counts.get('0', 0) / sum(counts.values())) * 100)

# 5. الرسم البياني للكشف الجنائي
plt.figure(figsize=(12, 6))
plt.plot(angles, fidelities, 'o-', label='استجابة الجهاز الحالية')
plt.axvline(0, color='red', linestyle='--', label='نقطة الصفر الأصلية')
plt.title("تحليل بصمة التصحيح الطوري (Phase Fingerprint Analysis)")
plt.xlabel("الزاوية المحقونة (راديان)")
plt.ylabel("الدقة %")
plt.legend()
plt.grid(True)
plt.show()
