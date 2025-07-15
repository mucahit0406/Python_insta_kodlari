import tkinter as tk
from tkinter import messagebox
import instaloader
import time

# Tkinter Penceresi Oluşturma
root = tk.Tk()
root.title("Instagram Takipçi Listesi Çekme")

# Hesap bilgileri için Label ve Text kutusu
hesap_label = tk.Label(root, text="Hesap bilgilerini girin (email,password):")
hesap_label.pack()

hesap_listbox = tk.Text(root, height=2, width=30)  # Hesap bilgileri için Text widget
hesap_listbox.pack()

# Kullanıcı adı için Label ve Entry kutusu
kullanici_label = tk.Label(root, text="Kullanıcı Adını Girin:")
kullanici_label.pack()

kullanici_entry = tk.Entry(root)
kullanici_entry.pack()

# Takipçi listesi çekme fonksiyonu
def takip_listesi_cek():
    global hesap_listbox  # Global değişken yapıyoruz
    hesap_text = hesap_listbox.get("1.0", tk.END).strip()  # Artık global olduğu için direkt erişiliyor
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

        # Takipçileri çekmek için iterator
        takipci_iterator = profile.get_followers()

        # Dosyaya yazma işlemi
        dosya_adi = f"{kullanici_adi}_takiplistesi.txt"
        with open(dosya_adi, "w") as f:
            for takipci in takipci_iterator:
                takipciler.append(takipci.username)
                f.write(f"{takipci.username}\n")
                sayac += 1

                # Her 1000 takipçide bir 30 saniye bekle
                if sayac % 1000 == 0:
                    f.flush()  # Dosyayı arada kaydet
                    print(f"{sayac} takipçi çekildi, 30 saniye bekleniyor...")
                    time.sleep(30)  # 30 saniye bekleme

        messagebox.showinfo("Başarılı", f"{kullanici_adi} adlı kullanıcının takipçileri {dosya_adi} dosyasına kaydedildi.")
    except Exception as e:
        messagebox.showerror("Hata", f"Takip listesi çekilemedi: {str(e)}")

# Takipçi listesini çekme butonu
cek_buton = tk.Button(root, text="Takip Listesini Çek", command=takip_listesi_cek)
cek_buton.pack()

root.mainloop()
