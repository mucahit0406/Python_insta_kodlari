def takip_listesi_cek():
    hesap_text = hesap_listbox.get("1.0", tk.END).strip()
    kullanici_adi = kullanici_entry.get().strip()

    if not hesap_text or not kullanici_adi:
        messagebox.showwarning("Uyarı", "Lütfen hesap bilgilerinizi ve kullanıcı adını girin.")
        return

    hesap_bilgileri = hesap_text.split(",")
    if len(hesap_bilgileri) != 2:
        messagebox.showwarning("Hata", "Hesap bilgilerini email,password formatında girin.")
        return

    email, sifre = hesap_bilgileri[0].strip(), hesap_bilgileri[1].strip()

    try:
        # Instaloader ile giriş yap
        loader = instaloader.Instaloader()
        loader.login(email, sifre)

        # Giriş başarılı, takip eden kişileri çekelim
        profile = instaloader.Profile.from_username(loader.context, kullanici_adi)
        takipciler = []
        sayac = 0

        # Takipçileri 2k kişi çektikten sonra bekleme ekleyerek topla
        toplam_takipci = profile.followers
        takipci_iterator = profile.get_followers()

        dosya_adi = f"{kullanici_adi}_takiplistesi.txt"
        with open(dosya_adi, "w") as f:
            for takipci in takipci_iterator:
                takipciler.append(takipci.username)
                f.write(f"{takipci.username}\n")
                sayac += 1

                # Her 2000 takipçide bir 30 saniye bekle
                if sayac % 2000 == 0:
                    f.flush()  # Dosyayı arada kaydet
                    print(f"{sayac} takipçi çekildi, 30 saniye bekleniyor...")
                    time.sleep(30)  # 30 saniye bekleme

        messagebox.showinfo("Başarılı", f"{kullanici_adi} adlı kullanıcının takipçileri {dosya_adi} dosyasına kaydedildi.")
    except Exception as e:
        messagebox.showerror("Hata", f"Takip listesi çekilemedi: {str(e)}")

def ac_takip_listesi_penceresi():
    # Yeni bir Toplevel penceresi oluştur
    takip_listesi_penceresi = tk.Toplevel(root)
    takip_listesi_penceresi.title("Instagram Takip Listesi Çekme")
    takip_listesi_penceresi.geometry("600x400")

    # Stil ayarları
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Helvetica", 12), foreground="#333", background="#e6f0f3")
    style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6, relief="flat", background="#3b5998",
                    foreground="white")
    style.map("TButton", background=[('active', '#3b4a68')])
    style.configure("TEntry", font=("Helvetica", 10))

    # Hesap ekleme alanı
    hesap_label = ttk.Label(takip_listesi_penceresi, text="Hesap Bilgileri (email,password formatında)")
    hesap_label.pack(pady=5)

    # hesap_listbox'ı bu pencereye ekle
    global hesap_listbox
    hesap_listbox = scrolledtext.ScrolledText(takip_listesi_penceresi, height=3, width=50)
    hesap_listbox.pack(pady=5)

    # Kullanıcı adı ekleme alanı
    kullanici_label = ttk.Label(takip_listesi_penceresi, text="Takip Listesi Çekilecek Kullanıcı Adı")
    kullanici_label.pack(pady=5)

    # kullanici_entry'yi bu pencereye ekle
    global kullanici_entry
    kullanici_entry = ttk.Entry(takip_listesi_penceresi, width=50)
    kullanici_entry.pack(pady=5)

    # Takip listesi çekme butonu
    takip_listesi_button = ttk.Button(takip_listesi_penceresi, text="Takip Listesini Çek", command=takip_listesi_cek, width=25)
    takip_listesi_button.pack(pady=20)
