import tkinter as tk
from tkinter import messagebox, scrolledtext
import instaloader
import os
from tkinter import ttk
from cryptography.fernet import Fernet

# Takip botu penceresini açan fonksiyon
def toplu_takip_programi():
    def takip_et():
        hesaplar_text = hesap_listbox.get("1.0", tk.END).strip().split("\n")
        takip_edilecek_text = takip_edilecek_listbox.get("1.0", tk.END).strip().split("\n")
        proxy_list_text = proxy_listbox.get("1.0", tk.END).strip().split("\n")

        if not hesaplar_text or not takip_edilecek_text or not proxy_list_text:
            messagebox.showwarning("Uyarı", "Lütfen hesapları, takip edilecekleri ve proxy'leri ekleyin.")
            return

        hesap_list = []

        # Hesapları ayır (proxy'ler ayrı bir listede)
        for hesap_sifre in hesaplar_text:
            hesap_bilgileri = hesap_sifre.split(",")
            if len(hesap_bilgileri) != 2:
                messagebox.showwarning("Hata", f"Geçersiz format: {hesap_sifre}. Doğru format: email,password")
                continue

            hesap_list.append((hesap_bilgileri[0].strip(), hesap_bilgileri[1].strip()))

        # 3 hesap için 1 proxy kullanacak şekilde döngü
        for i, (hesap, sifre) in enumerate(hesap_list):
            proxy = proxy_list_text[i // 3]  # Her 3 hesap için aynı proxy'yi kullan

            try:
                # Instaloader ile giriş
                loader = instaloader.Instaloader()

                # Proxy ayarı
                loader.context.session.proxies = {"http": proxy, "https": proxy}

                loader.login(hesap, sifre)

                # Giriş başarılı, takip etme işlemini yapalım
                session = loader.context._session  # Instaloader session'ını al
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "X-CSRFToken": session.cookies.get_dict()['csrftoken'],
                    "Referer": "https://www.instagram.com/",
                }

                for takip in takip_edilecek_text:
                    try:
                        profile = instaloader.Profile.from_username(loader.context, takip.strip())
                        follow_url = f"https://www.instagram.com/web/friendships/{profile.userid}/follow/"
                        response = session.post(follow_url, headers=headers)

                        if response.status_code == 200:
                            print(f"{hesap} -> {takip} takip edildi.")
                        else:
                            print(f"{hesap} -> {takip} takip edilemedi. Hata: {response.status_code}")
                    except Exception as e:
                        print(f"{takip} takip edilemedi: {e}")

                messagebox.showinfo("Başarılı", f"{hesap} için takip işlemi tamamlandı.")
            except Exception as e:
                messagebox.showerror("Hata", f"{hesap} için hata: {str(e)}")

    style = ttk.Style()
    style.theme_use("clam")

    # Etiketler
    style.configure("TLabel", font=("Helvetica", 12), foreground="#333", background="#e6f0f3")

    # Butonlar
    style.configure("TButton", font=("Helvetica", 12), padding=8, relief="flat", background="#007bff",
                    foreground="white")
    style.map("TButton", background=[('active', '#0056b3')])

    # Giriş Alanları
    style.configure("TEntry", font=("Helvetica", 12), padding=6)

    # Yeni bir pencere oluştur
    takip_bot_penceresi = tk.Toplevel(root)
    takip_bot_penceresi.title("Instagram Takip Botu")
    takip_bot_penceresi.geometry("600x800")
    takip_bot_penceresi.configure(bg="#e6f0f3")  # Pencere arka plan rengini ayarla

    # Hesap ekleme alanı
    hesap_label = tk.Label(takip_bot_penceresi, text="Hesaplar (mail@gmail.com,şifre formatında)", bg="#e6f0f3")
    hesap_label.pack(pady=10)

    global hesap_listbox
    hesap_listbox = scrolledtext.ScrolledText(takip_bot_penceresi, height=10, width=50, font=("Helvetica", 12))
    hesap_listbox.pack(pady=10)

    # Proxy ekleme alanı
    proxy_label = tk.Label(takip_bot_penceresi, text="Proxy Listesi (her satıra bir proxy)", bg="#e6f0f3")
    proxy_label.pack(pady=10)

    global proxy_listbox
    proxy_listbox = scrolledtext.ScrolledText(takip_bot_penceresi, height=5, width=50, font=("Helvetica", 12))
    proxy_listbox.pack(pady=10)

    # Takip edilecek hesaplar alanı
    takip_edilecek_label = tk.Label(takip_bot_penceresi, text="Takip Edilecek Hesaplar (sadece profil adları)",
                                    bg="#e6f0f3")
    takip_edilecek_label.pack(pady=10)

    global takip_edilecek_listbox
    takip_edilecek_listbox = scrolledtext.ScrolledText(takip_bot_penceresi, height=10, width=50, font=("Helvetica", 12))
    takip_edilecek_listbox.pack(pady=10)

    # Takip et butonu
    takip_button = tk.Button(takip_bot_penceresi, text="Takip Et", command=takip_et)
    takip_button.pack(pady=20)


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
        takipciler = [follower.username for follower in profile.get_followers()]

        # Takip listesi dosyasını kaydet
        dosya_adi = f"{kullanici_adi}_takiplistesi.txt"
        with open(dosya_adi, "w") as f:
            for takipci in takipciler:
                f.write(f"{takipci}\n")

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



# Gönderi Yorum ve Beğeni Programı
def toplu_yorum_programi():
    def yorum_at():
        hesaplar_text = hesap_listbox.get("1.0", tk.END).strip().split("\n")
        url_list_text = url_listbox.get("1.0", tk.END).strip().split("\n")
        yorum_text = yorum_listbox.get("1.0", tk.END).strip().split("\n")
        proxy_list_text = proxy_listbox.get("1.0", tk.END).strip().split("\n")
        begen = begen_var.get()  # Gönderi beğenilsin mi seçeneği

        if not hesaplar_text or not url_list_text or not yorum_text or not proxy_list_text:
            messagebox.showwarning("Uyarı", "Lütfen hesapları, URL'leri, yorumları ve proxy'leri ekleyin.")
            return

        hesap_list = []

        # Hesapları ayır (proxy'ler ayrı bir listede)
        for hesap_sifre in hesaplar_text:
            hesap_bilgileri = hesap_sifre.split(",")
            if len(hesap_bilgileri) != 2:
                messagebox.showwarning("Hata", f"Geçersiz format: {hesap_sifre}. Doğru format: email,password")
                continue

            hesap_list.append((hesap_bilgileri[0].strip(), hesap_bilgileri[1].strip()))

        # 3 hesap için 1 proxy kullanacak şekilde döngü
        for i, (hesap, sifre) in enumerate(hesap_list):
            proxy = proxy_list_text[i // 3]  # Her 3 hesap için aynı proxy'yi kullan

            try:
                # Instaloader ile giriş
                loader = instaloader.Instaloader()

                # Proxy ayarı
                loader.context._session.proxies = {"http": proxy, "https": proxy}

                loader.login(hesap, sifre)

                # Giriş başarılı, yorum ve beğeni işlemini yapalım
                session = loader.context._session  # Instaloader session'ını al
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "X-CSRFToken": session.cookies.get_dict()['csrftoken'],
                    "Referer": "https://www.instagram.com/",
                }

                for url, yorum in zip(url_list_text, yorum_text):
                    try:
                        # Gönderiye yorum atma
                        media_id = instaloader.Post.from_shortcode(loader.context, url.strip().split('/')[-2]).mediaid
                        comment_url = f"https://www.instagram.com/web/comments/{media_id}/add/"
                        data = {"comment_text": yorum.strip()}
                        response = session.post(comment_url, data=data, headers=headers)

                        if response.status_code == 200:
                            print(f"{hesap} -> {url} yorum yapıldı: {yorum}")
                        else:
                            print(f"{hesap} -> {url} yorum yapılamadı. Hata: {response.status_code}")

                        # Eğer beğenilmesi isteniyorsa
                        if begen:
                            like_url = f"https://www.instagram.com/web/likes/{media_id}/like/"
                            like_response = session.post(like_url, headers=headers)

                            if like_response.status_code == 200:
                                print(f"{hesap} -> {url} beğenildi.")
                            else:
                                print(f"{hesap} -> {url} beğenilemedi. Hata: {like_response.status_code}")
                    except Exception as e:
                        print(f"{url} işlem yapılamadı: {e}")

                messagebox.showinfo("Başarılı", f"{hesap} için işlem tamamlandı.")
            except Exception as e:
                messagebox.showerror("Hata", f"{hesap} için hata: {str(e)}")

    # Stil ayarları
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Helvetica", 12), foreground="#333", background="#e6f0f3")
    style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6, relief="flat", background="#3b5998", foreground="white")
    style.map("TButton", background=[('active', '#3b4a68')])
    style.configure("TEntry", font=("Helvetica", 10))

    # Yeni bir pencere oluştur
    yorum_bot_penceresi = tk.Toplevel(root)
    yorum_bot_penceresi.title("Instagram Yorum ve Beğeni Botu")
    yorum_bot_penceresi.geometry("600x800")

    # Hesap ekleme alanı
    hesap_label = ttk.Label(yorum_bot_penceresi, text="Hesaplar (mail@gmail.com,şifre formatında)")
    hesap_label.pack(pady=5)

    hesap_listbox = scrolledtext.ScrolledText(yorum_bot_penceresi, height=10, width=50)
    hesap_listbox.pack(pady=5)

    # Proxy ekleme alanı
    proxy_label = ttk.Label(yorum_bot_penceresi, text="Proxy Listesi (her satıra bir proxy)")
    proxy_label.pack(pady=5)

    proxy_listbox = scrolledtext.ScrolledText(yorum_bot_penceresi, height=5, width=50)
    proxy_listbox.pack(pady=5)

    # URL ekleme alanı
    url_label = ttk.Label(yorum_bot_penceresi, text="Gönderi URL'leri (her satıra bir URL)")
    url_label.pack(pady=5)

    url_listbox = scrolledtext.ScrolledText(yorum_bot_penceresi, height=5, width=50)
    url_listbox.pack(pady=5)

    # Yorum ekleme alanı
    yorum_label = ttk.Label(yorum_bot_penceresi, text="Yorumlar (her satıra bir yorum)")
    yorum_label.pack(pady=5)

    yorum_listbox = scrolledtext.ScrolledText(yorum_bot_penceresi, height=5, width=50)
    yorum_listbox.pack(pady=5)

    # Beğeni seçeneği
    begen_var = tk.BooleanVar()
    begen_checkbox = ttk.Checkbutton(yorum_bot_penceresi, text="Gönderiyi Beğen", variable=begen_var)
    begen_checkbox.pack(pady=10)

    # Yorum at butonu
    yorum_button = ttk.Button(yorum_bot_penceresi, text="Yorum At", command=yorum_at)
    yorum_button.pack(pady=20)




def ac_takip_takipci_penceresi():
    takip_pencere = tk.Toplevel()
    takip_pencere.title("Takip ve Takipçileri Bul")
    takip_pencere.geometry("600x400")
    takip_pencere.configure(bg="#e6f0f3")

    # Stil ayarları
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Helvetica", 12), foreground="#333", background="#e6f0f3")
    style.configure("TButton", font=("Helvetica", 10, "bold"), padding=6, relief="flat", background="#3b5998",
                    foreground="white")
    style.map("TButton", background=[('active', '#3b4a68')])  # Aktif buton rengi
    style.configure("TEntry", font=("Helvetica", 10), padding=5)

    # Başlık
    baslik_label = ttk.Label(takip_pencere, text="Takip Edilen ve Takip Edenleri Bul(Hedef Kişinin)", style="TLabel")
    baslik_label.pack(pady=10)

    # Kullanıcı adı girişi
    username_label = ttk.Label(takip_pencere, text="Kullanıcı Adınızı Girin:", style="TLabel")
    username_label.pack(pady=5)
    username_entry = ttk.Entry(takip_pencere, style="TEntry")
    username_entry.pack(pady=5)

    # Şifre girişi
    password_label = ttk.Label(takip_pencere, text="Şifrenizi Girin:", style="TLabel")
    password_label.pack(pady=5)
    password_entry = ttk.Entry(takip_pencere, show='*', style="TEntry")  # Şifreyi gizlemek için
    password_entry.pack(pady=5)

    # Kişi adı girişi
    kisi_label = ttk.Label(takip_pencere, text="Kişinin Kullanıcı Adını Girin:", style="TLabel")
    kisi_label.pack(pady=5)
    kisi_entry = ttk.Entry(takip_pencere, style="TEntry")
    kisi_entry.pack(pady=5)


    # Takip edenleri bul fonksiyonu
    def takip_edenleri_bul():
        username = username_entry.get()
        password = password_entry.get()
        kisi = kisi_entry.get()

        try:
            L = instaloader.Instaloader()
            L.login(username, password)  # Kullanıcı giriş yapar
            profile = instaloader.Profile.from_username(L.context, kisi)

            takipciler = [follower.username for follower in profile.get_followers()]
            messagebox.showinfo("Takip Edenler", f"{kisi} kişisinin takip edenleri:\n" + ", ".join(takipciler))
        except Exception as e:
            messagebox.showerror("Hata", str(e))

        # Takip ettiklerini bul fonksiyonu

    def takip_ettiklerini_bul():
        username = username_entry.get()
        password = password_entry.get()
        kisi = kisi_entry.get()

        try:
            L = instaloader.Instaloader()
            L.login(username, password)  # Kullanıcı giriş yapar
            profile = instaloader.Profile.from_username(L.context, kisi)

            takip_ettikleri = [following.username for following in profile.get_followees()]
            messagebox.showinfo("Takip Ettikleri", f"{kisi} kişisinin takip ettikleri:\n" + ", ".join(takip_ettikleri))
        except Exception as e:
            messagebox.showerror("Hata", str(e))

        # Butonlar (Takip edenler ve ettiklerini bulma)

    takip_ettiklerini_bul_button = ttk.Button(takip_pencere, text="Takip Ettiklerini Bul", style="TButton",
                                              command=takip_ettiklerini_bul)
    takip_ettiklerini_bul_button.pack(pady=20)

    takip_edenleri_bul_button = ttk.Button(takip_pencere, text="Takip Edenleri Bul", style="TButton",
                                           command=takip_edenleri_bul)
    takip_edenleri_bul_button.pack(pady=20)



# Öne çıkanları çekme işlemi
def one_cikanlari_cek():
    new_window = tk.Toplevel(root)
    new_window.title("Öne Çıkanları Çek")
    new_window.geometry("400x300")

    def cek_one_cikanlar():
        username = username_entry.get()
        password = password_entry.get()
        hedef_kullanici = kisi_entry.get()

        try:
            # Instaloader objesi oluştur
            L = instaloader.Instaloader()

            # Kullanıcı ile giriş yap
            L.login(username, password)

            # Profil bilgilerini al
            profile = instaloader.Profile.from_username(L.context, hedef_kullanici)

            # Öne çıkan hikayeleri indir
            klasor_adi = f"{hedef_kullanici}_one_cikanlar"
            if not os.path.exists(klasor_adi):
                os.makedirs(klasor_adi)

            for highlight in L.get_highlights(profile):
                for item in highlight.get_items():
                    L.download_storyitem(item, target=klasor_adi)

            messagebox.showinfo("Başarılı", f"{hedef_kullanici} kişisinin öne çıkanları '{klasor_adi}' klasörüne kaydedildi.")
            new_window.destroy()
        except Exception as e:
            messagebox.showerror("Hata", str(e))

    # Kullanıcı adı ve şifre giriş alanları

    # Tema stilleri
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Helvetica", 12), foreground="#333", background="#e6f0f3")
    style.configure("TButton", font=("Helvetica", 10), padding=6, relief="flat", background="#3b5998", foreground="white")
    style.configure("TEntry", font=("Helvetica", 10))

    # Kullanıcı adı
    username_label = ttk.Label(new_window, text="Kullanıcı adınızı girin:")
    username_label.pack(pady=5)
    username_entry = ttk.Entry(new_window)
    username_entry.pack(pady=5)

    # Şifre
    password_label = ttk.Label(new_window, text="Şifrenizi girin:")
    password_label.pack(pady=5)
    password_entry = ttk.Entry(new_window, show='*')
    password_entry.pack(pady=5)

    # Kişi adı
    kisi_label = ttk.Label(new_window, text="Kişinin kullanıcı adını girin:")
    kisi_label.pack(pady=5)
    kisi_entry = ttk.Entry(new_window)
    kisi_entry.pack(pady=5)

    # Öne çıkanları çek butonu
    cek_button = ttk.Button(new_window, text="Öne Çıkanları Çek", command=lambda: cek_one_cikanlar())
    cek_button.pack(pady=20)

# Ana pencereyi başlat
root = tk.Tk()
root.title("Instagram İşlemleri")
root.geometry("550x450")

# Tema stilleri
style = ttk.Style()
style.theme_use("clam")  # 'clam', 'alt', 'default', 'classic' gibi temalar kullanılabilir.
style.configure("TLabel", font=("Helvetica", 12), foreground="#333")
style.configure("TButton", font=("Helvetica", 10), padding=6, relief="flat", background="#3b5998", foreground="white")

# Pencere arka planını renklendirme
root.configure(bg="#e6f0f3")  # Soluk mavi-gri arka plan rengi

# Başlık ve seçenekler
baslik_label = ttk.Label(root, text="HOŞGELDİNİZ", font=("Helvetica", 16, "bold"), background="#e6f0f3", foreground="#3b5998")
baslik_label.pack(pady=10)

secenek_label = ttk.Label(root, text="Yapmak istediğiniz işlemi seçin", font=("Helvetica", 14), background="#e6f0f3", foreground="#333")
secenek_label.pack(pady=10)

# Butonlar
one_cikanlari_cek_button = ttk.Button(root, text="Kişinin Öne Çıkanlarını Çek", width=25, command=lambda: one_cikanlari_cek())
one_cikanlari_cek_button.place(x=300, y=200)

takip_takipci_islemleri_button = ttk.Button(root, text="Takip ve Takipçilerini Bul(Hedef Kişinin)", width=25, command=lambda: ac_takip_takipci_penceresi())
takip_takipci_islemleri_button.place(x=50, y=100)

toplu_takip_button = ttk.Button(root, text="Toplu Takip Ettirme", width=25, command=lambda: toplu_takip_programi())
toplu_takip_button.place(x=300, y=100)

yorum_attirma_button = ttk.Button(root, text="Gönderiye Yorum ve Beğeni", width=25, command=lambda: toplu_yorum_programi())
yorum_attirma_button.place(x=50, y=200)

# Ana döngü
root.mainloop()
