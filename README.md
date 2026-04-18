Prompt Optimization Agent
📌 Overview

Prompt Optimization Agent, kullanıcıların yazdığı ham promptları analiz ederek daha açık, etkili ve sonuç odaklı hale getiren bir yardımcı AI aracıdır.

Bu agent, özellikle Code Assist Agent ve MailCraft (Email Generator) gibi üretim odaklı agent’larda daha kaliteli çıktılar elde edilmesini sağlar.

Kullanıcının sorduğu soruya şu perspektiften yaklaşır:
👉 “Bu isteği LLM’e daha iyi nasıl anlatabiliriz?”

🎯 Purpose

Bu agent’ın temel amacı:

Kullanıcı promptlarını daha net, anlaşılır ve yapılandırılmış hale getirmek
LLM çıktılarının kalitesini ve doğruluğunu artırmak
Non-technical kullanıcıların bile doğru prompt yazabilmesini sağlamak
Tüm AI Hub agent’larının performansını dolaylı olarak yükseltmek
⚙️ How It Works
User Input
Kullanıcı ham promptunu girer
(Opsiyonel) Hangi agent için kullanılacağını seçer
Code Assist
MailCraft
General Purpose
Prompt Analysis
Prompt aşağıdaki kriterlere göre analiz edilir:
Belirsizlik (ambiguity)
Eksik bağlam (missing context)
Yapısal zayıflık
Output beklentisinin net olmaması
Optimization Engine
Prompt aşağıdaki tekniklerle iyileştirilir:
Context ekleme
Rol tanımlama (e.g. "You are a senior developer...")
Format belirleme (bullet, JSON, step-by-step)
Constraint ekleme (limitler, ton, dil vs.)
Output Generation
Kullanıcıya 3 farklı çıktı sunulur:
✨ Optimized Prompt (Direkt kullanılabilir versiyon)
🔍 Improvement Explanation (Neler değişti?)
⚡ Quick Tips (Benzer promptlar için öneriler)
🧩 Key Features
Agent-aware optimization
Code Assist için teknik detay artırımı
MailCraft için ton ve yapı optimizasyonu
Multi-language support
Türkçe prompt → İngilizce optimize
veya aynı dilde iyileştirme
Structured prompt generation
Step-by-step
JSON format
Instruction-based prompts
Beginner-friendly
Teknik bilgisi olmayan kullanıcılar için açıklayıcı öneriler
🖥️ Example Use Cases
1. Code Assist için

Input:

python kodu yaz api çağıran

Optimized Prompt:

You are a senior Python developer.

Write a clean and production-ready Python script that sends a GET request to a REST API.

Requirements:
- Use requests library
- Include error handling
- Print response in JSON format
- Add comments for each step
2. MailCraft için

Input:

müşteriye gecikme için mail yaz

Optimized Prompt:

Write a professional apology email to a customer regarding a delay in service.

Details:
- Tone: polite and reassuring
- Include apology and explanation
- Offer next steps or resolution
- Keep it concise (max 150 words)
3. General Use

Input:

bana marketing fikri ver

Optimized Prompt:

You are a marketing strategist.

Generate 5 creative digital marketing campaign ideas for a fintech company.

Constraints:
- Target audience: young professionals (25-35)
- Channels: social media + email
- Each idea should include a short explanation
🧠 Why It Matters
Aynı model → daha iyi prompt = çok daha iyi output
Kullanıcıların LLM kullanımındaki en büyük problemi:
👉 “Ne sormalıyım?”

Bu agent bu problemi çözer.

🔗 Integration in AI Hub

Prompt Optimization Agent:

Tüm agent’ların önünde bir “booster layer” olarak konumlanabilir
Kullanıcı, herhangi bir agent’a gitmeden önce promptunu optimize edebilir
veya agent içinde inline öneri sistemi olarak çalışabilir
⚠️ Current Limitations
Domain-specific çok teknik promptlarda manuel düzenleme gerekebilir
Çok kısa inputlarda (1-2 kelime) tahmin bazlı iyileştirme yapılır
%100 doğru intent çıkarımı her zaman garanti değildir
🚀 Future Improvements (Phase 2 - Not Active Yet)
Prompt scoring system (quality score /100)
Auto A/B testing of prompts
Agent-specific prompt templates
Learning from user feedback (feedback loop)
Prompt history & reuse system
Fine-tuned prompt optimization models
🧩 Deployment Note
UI Streamlit ile geliştirilmiştir
Henüz merkezi bir sunucuya deploy edilmemiştir
AI Hub üzerinden erişilebilir hale getirilmesi planlanmaktadır
