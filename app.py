import streamlit as st
import math
import matplotlib.pyplot as plt
import pandas as pd

# Sayfa ayarları
st.set_page_config(page_title="Perakendeci Stok Bilgi Sistemi", page_icon="📦", layout="centered")

st.title("📦 Perakendeci Stok Modelleri Bilgi Sistemi")
st.write("Soruları yanıtlayarak probleminize uygun modeli belirleyin, parametreleri girin ve tek tuşla optimum çözümü elde edin.")

st.divider()

# ==========================================
# 1. ADIM: KULLANICIYI DOĞRU MODELE YÖNLENDİRME
# ==========================================
st.subheader("1. Adım: Model Belirleme")

sonradan_karsilama = st.radio(
    "Stoklarınız tükendiğinde talebin sonradan karşılanmasına (yoksatmaya) izin veriliyor mu?",
    (
        "Hayır, sonradan karşılama yok (Model 4 - Klasik EOQ)",
        "Evet, sonradan karşılama var (Model 3 - Perakendeci Modeli)"
    )
)

pi_var_mi = False
if "Model 3" in sonradan_karsilama:
    pi_durumu = st.radio(
        "Zamana bağlı sonradan karşılama maliyetine (π̂) ek olarak, zamandan bağımsız (birim başına sabit) ceza maliyeti (π) var mı?",
        (
            "Hayır, zamandan bağımsız maliyet YOK (Sadece π̂ var)",
            "Evet, zamandan bağımsız maliyet VAR (Hem π̂ hem π var)"
        )
    )
    if "VAR" in pi_durumu:
        pi_var_mi = True

st.divider()

# ==========================================
# 2. ADIM: PARAMETRE GİRİŞİ
# ==========================================
st.subheader("2. Adım: Problem Parametreleri")

# Temel Parametreler (D ve A)
col1, col2 = st.columns(2)
with col1:
    D = st.number_input("Yıllık Talep (D) [adet/yıl]", min_value=0.01, value=1000.0, step=50.0)
with col2:
    A = st.number_input("Sipariş Verme Maliyeti (A) [TL/sipariş]", min_value=0.01, value=100.0, step=10.0)

# Stokta Bulundurma Maliyeti (h) Seçeneği
h_durumu = st.radio(
    "Stokta bulundurma maliyeti (h) doğrudan verilmiş mi?",
    (
        "Evet, h değeri doğrudan verilmiş",
        "Hayır, h verilmemiş (i ve C değerleri ile h = i × C hesaplanacak)"
    ),
    horizontal=True
)

if "Evet" in h_durumu:
    c_h1, c_h2 = st.columns(2)
    with c_h1:
        h = st.number_input("Stokta Bulundurma Maliyeti (h) [TL/adet-yıl]", min_value=0.01, value=5.0, step=0.5)
    with c_h2:
        C = st.number_input(
            "Birim Satın Alma Maliyeti (C) [TL/adet] (Opsiyonel)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            help="Problemde satın alma maliyeti verilmemişse veya toplama dahil edilmeyecekse 0 bırakın."
        )
else:
    c_ic1, c_ic2 = st.columns(2)
    with c_ic1:
        C = st.number_input("Birim Satın Alma Maliyeti (C) [TL/adet]", min_value=0.01, value=25.0, step=1.0)
    with c_ic2:
        i_yuzde = st.number_input(
            "Stokta Bulundurma Maliyet Oranı (i) [%]",
            min_value=0.01,
            max_value=1000.0,
            value=20.0,
            step=1.0,
            help="Örneğin %20 için 20 yazın."
        )
    i_oran = i_yuzde / 100.0
    h = i_oran * C
    st.info(f"📌 Hesaplanan Stokta Bulundurma Maliyeti: **h = i × C = {i_oran:.2f} × {C:.2f} = {h:.4f} TL/adet-yıl**")

# Model 3'e Özel Parametreler (π̂ ve π)
if "Model 3" in sonradan_karsilama:
    c_m3_1, c_m3_2 = st.columns(2)
    with c_m3_1:
        pi_hat = st.number_input("Zamana Bağlı Sonradan Karşılama Maliyeti (π̂) [TL/adet-yıl]", min_value=0.01, value=15.0, step=1.0)
    with c_m3_2:
        if pi_var_mi:
            pi_sabit = st.number_input("Zamandan Bağımsız Sonradan Karşılama Maliyeti (π) [TL/adet]", min_value=0.0, value=2.0, step=0.5)
        else:
            pi_sabit = 0.0

st.divider()

# ==========================================
# GRAFİK ÇİZİM FONKSİYONU
# ==========================================
def stok_grafigi_ciz(Q_opt, b_opt, T, t1, t2, model_adi):
    fig, ax = plt.subplots(figsize=(8, 3.8))
    
    I_max = Q_opt - b_opt
    if b_opt == 0:
        x = [0, 0, T, T, 2*T]
        y = [0, Q_opt, 0, Q_opt, 0]
    else:
        x = [0, 0, t1, T, T, T + t1, 2*T]
        y = [0, I_max, 0, -b_opt, I_max, 0, -b_opt]

    ax.plot(x, y, color="#1f77b4", linewidth=2, label="Stok Seviyesi")
    ax.axhline(0, color="black", linewidth=1)
    ax.fill_between(x, y, 0, where=[val >= 0 for val in y], color="#1f77b4", alpha=0.15, label="Elde Bulunan Stok")
    if b_opt > 0:
        ax.fill_between(x, y, 0, where=[val <= 0 for val in y], color="#d62728", alpha=0.2, label="Sonradan Karşılama (b)")

    ax.set_title(f"{model_adi} - Stok Seviyesi Grafiği (2 Çevrim)")
    ax.set_xlabel("Zaman (Yıl)")
    ax.set_ylabel("Stok Miktarı (Adet)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper right")
    return fig

# ==========================================
# 3. ADIM: TEK TUŞLA HESAPLAMA VE ÇIKTI
# ==========================================
if st.button("🚀 Optimum Sonuçları Hesapla", type="primary", use_container_width=True):
    st.subheader("3. Adım: Hesaplama Sonuçları")

    # --- MODEL 4 (KLASİK EOQ) ---
    if "Model 4" in sonradan_karsilama:
        Q_opt = math.sqrt((2 * D * A) / h)
        I_ort = Q_opt / 2
        T = Q_opt / D
        T_gun = T * 365
        N = D / Q_opt

        siparis_mlyt = (D / Q_opt) * A
        stok_mlyt = I_ort * h
        satinalma_mlyt = D * C
        K_Q = siparis_mlyt + stok_mlyt + satinalma_mlyt

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Optimum Sipariş (Q*)", f"{Q_opt:.2f} adet")
        c2.metric("Ortalama Stok (Ī)", f"{I_ort:.2f} adet")
        c3.metric("Çevrim Süresi (T)", f"{T_gun:.1f} gün")
        c4.metric("Toplam Maliyet K(Q)", f"{K_Q:,.2f} TL")

        st.success(
            f"**Karar Özeti:** En ekonomik çözüm için her **{T_gun:.1f} günde bir** (yılda {N:.1f} kez) "
            f"yaklaşık **{Q_opt:.0f} adet** sipariş vermelisiniz. Toplam yıllık maliyetiniz **{K_Q:,.2f} TL** olacaktır."
        )

        maliyet_satirlari = [
            ["Sipariş Verme Maliyeti ((D/Q)·A)", f"{siparis_mlyt:,.2f}"],
            ["Stokta Bulundurma Maliyeti ((Q/2)·h)", f"{stok_mlyt:,.2f}"],
        ]
        if C > 0:
            maliyet_satirlari.append(["Satın Alma Maliyeti (D·C)", f"{satinalma_mlyt:,.2f}"])
        maliyet_satirlari.append(["TOPLAM MALİYET K(Q)", f"{K_Q:,.2f}"])

        df_maliyet = pd.DataFrame(maliyet_satirlari, columns=["Maliyet Kalemi", "Tutar (TL/Yıl)"])
        st.table(df_maliyet)
        st.pyplot(stok_grafigi_ciz(Q_opt, 0, T, T, 0, "Model 4 (EOQ)"))

    # --- MODEL 3 (SONRADAN KARŞILAMALI PERAKENDECİ MODELİ) ---
    else:
        if not pi_var_mi:
            Q_opt = math.sqrt(((2 * A * D) / h) * ((h + pi_hat) / pi_hat))
            b_opt = Q_opt * (h / (h + pi_hat))
            model_baslik = "Model 3 (π = 0)"
        else:
            kok_ici = ((2 * A * D) / h) - (((pi_sabit * D) ** 2) / (h * (h + pi_hat)))
            if kok_ici <= 0:
                st.error(
                    "⚠️ **Uyarı:** Girilen zamandan bağımsız sonradan karşılama maliyeti (π) çok yüksek olduğu için "
                    "sonradan karşılama yapmak ekonomik değildir (kök içi negatif/sıfır). "
                    "Bu problemde **Model 4 (Yoksatmasız EOQ)** kullanmalısınız."
                )
                st.stop()

            Q_opt = math.sqrt(kok_ici) * math.sqrt((h + pi_hat) / pi_hat)
            b_opt = (h * Q_opt - pi_sabit * D) / (h + pi_hat)

            if b_opt <= 0:
                st.warning(
                    "⚠️ **Uyarı:** Hesaplanan b* ≤ 0 çıktı. Bu π değeriyle müşteriyi bekletmek (sonradan karşılama) "
                    "ekonomik değildir; sistem otomatik olarak yoksatmasız çözüme (Model 4) yakınsar."
                )
                st.stop()
            model_baslik = "Model 3 (π > 0)"

        I_max = Q_opt - b_opt
        I_ort = ((Q_opt - b_opt) ** 2) / (2 * Q_opt)
        B_ort = (b_opt ** 2) / (2 * Q_opt)
        
        t1 = (Q_opt - b_opt) / D
        t2 = b_opt / D
        T = t1 + t2
        N = D / Q_opt

        siparis_mlyt = (D / Q_opt) * A
        stok_mlyt = I_ort * h
        zamana_bagli_mlyt = B_ort * pi_hat
        zamandan_bagimsiz_mlyt = (D / Q_opt) * pi_sabit * b_opt
        satinalma_mlyt = D * C
        K_Qb = siparis_mlyt + stok_mlyt + zamana_bagli_mlyt + zamandan_bagimsiz_mlyt + satinalma_mlyt

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Optimum Sipariş (Q*)", f"{Q_opt:.2f} adet")
        c2.metric("Maks. Yoksatma (b*)", f"{b_opt:.2f} adet")
        c3.metric("Maks. Stok (Q*-b*)", f"{I_max:.2f} adet")
        c4.metric("Toplam Maliyet K(Q,b)", f"{K_Qb:,.2f} TL")

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Ortalama Stok (Ī)", f"{I_ort:.2f} adet")
        c6.metric("Ort. Yoksatma (B̄)", f"{B_ort:.2f} adet")
        c7.metric("Stoklu Süre (t1)", f"{t1*365:.1f} gün")
        c8.metric("Yoksatma Süresi (t2)", f"{t2*365:.1f} gün")

        st.success(
            f"**Karar Özeti:** Her **{T*365:.1f} günde bir** (yılda {N:.1f} kez) **{Q_opt:.0f} adet** sipariş vermelisiniz. "
            f"Stoklarınız **{t1*365:.1f} gün** boyunca talebi karşılayacak, kalan **{t2*365:.1f} günde** ise en fazla "
            f"**{b_opt:.0f} adet** talep sonradan karşılanmak üzere bekletilecektir. Toplam yıllık maliyet: **{K_Qb:,.2f} TL**."
        )

        maliyet_satirlari = [
            ["Sipariş Verme Maliyeti ((D/Q)·A)", f"{siparis_mlyt:,.2f}"],
            ["Stokta Bulundurma Maliyeti (Ī·h)", f"{stok_mlyt:,.2f}"],
            ["Zamana Bağlı Sonradan Karş. Maliyeti (B̄·π̂)", f"{zamana_bagli_mlyt:,.2f}"],
        ]
        if pi_var_mi:
            maliyet_satirlari.append(["Zamandan Bağımsız Sonradan Karş. Maliyeti ((D/Q)·π·b)", f"{zamandan_bagimsiz_mlyt:,.2f}"])
        if C > 0:
            maliyet_satirlari.append(["Satın Alma Maliyeti (D·C)", f"{satinalma_mlyt:,.2f}"])
        maliyet_satirlari.append(["TOPLAM MALİYET K(Q,b)", f"{K_Qb:,.2f}"])

        df_maliyet = pd.DataFrame(maliyet_satirlari, columns=["Maliyet Kalemi", "Tutar (TL/Yıl)"])
        st.table(df_maliyet)
        st.pyplot(stok_grafigi_ciz(Q_opt, b_opt, T, t1, t2, model_baslik))
