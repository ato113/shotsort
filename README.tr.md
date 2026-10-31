# shotsort

*Türkçe · [English](README.md)*

**Ekran görüntülerini, içlerinde ne yazdığına göre yeniden adlandır ve düzenle.**

[![CI](https://github.com/ato113/shotsort/actions/workflows/ci.yml/badge.svg)](https://github.com/ato113/shotsort/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Lisans: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Ekran görüntüleri klasörün bir `Screenshot_20261014_184412.png` duvarı. İçinde
hiçbir şey bulamıyorsun, çünkü isimler hiçbir şey anlatmıyor. `shotsort`, her
ekran görüntüsünün içindeki metni OCR ile okur ve dosyayı **ne gösterdiğine göre**
adlandırır.

```console
$ shotsort suggest ~/Pictures/Screenshots

3 screenshot(s) would be renamed:

  Screenshot_2026-10-01.png  ->  2026-10-01_quarterly-revenue-report.png
  Screenshot_2026-10-02.png  ->  2026-10-02_install-python-on-windows.png
  Ekran Goruntusu 3.png      ->  2026-10-03_toplanti-notlari.png

This was a preview. Run 'shotsort apply' to do it.
```

Tarih dosyadan gelir; gerisi `shotsort`'un görüntü içinde okuduğu başlıktan.
Klasör birden aranabilir hale gelir.

## Kurulum

OCR için [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html)
gerekir (o olmadan shotsort yine tarihe göre düzenler — sadece metni okuyamaz):

```bash
# Tesseract: apt install tesseract-ocr  /  brew install tesseract  /  choco install tesseract
pip install shotsort
```

Ya da kaynaktan:

```bash
git clone https://github.com/ato113/shotsort
cd shotsort
pip install -e .
shotsort --version
```

## Kullanım

```bash
shotsort suggest ~/Pictures/Screenshots      # önizleme (hiçbir şey taşınmaz)
shotsort apply   ~/Pictures/Screenshots      # uygula (önce sorar)
shotsort undo                                # son çalıştırmayı geri al
```

Kullanışlı bayraklar:

| Bayrak | Anlamı |
|--------|--------|
| `-m`, `--by-month` | Sonuçları `YYYY-MM/` klasörlerine yerleştir |
| `-r`, `--recursive` | Alt klasörleri de dahil et |
| `-a`, `--all-images` | Sadece ekran görüntüsü gibi görünenleri değil, hepsini |
| `-l`, `--lang` | OCR dilleri, `+` ile ayrık (varsayılan `tur+eng`) |
| `--no-ocr` | Sadece tarihli isim, OCR'ı atla |
| `-y`, `--yes` | `apply`'da onayı atla |

## İsim nasıl seçilir

1. **Tarih** — dosyanın değiştirilme zamanından, `YYYY-AA-GG` olarak.
2. **Başlık** — OCR metni yukarıdan aşağıya döndürür, yani arayüz gürültüsünden
   (saat, pil, menü çubukları) sonraki ilk anlamlı satır neredeyse her zaman
   başlıktır. shotsort o gürültüyü eler ve ilk gerçek satırı alır.
3. **Slug** — küçük harf, Türkçe karakterler ASCII'ye çevrilir (`Toplantı` →
   `toplanti`) ki isim her dosya sisteminde güvenli olsun, birkaç kelimeye
   kırpılır.

Kullanılabilir metin yok mu? Dosya yine temiz bir `YYYY-AA-GG_screenshot.png`
adı alır.

## Tasarımdan güvenli

- `suggest` hiçbir şeyi değiştirmez; planı her zaman önce görürsün.
- `apply` her taşımayı kaydeder, `undo` hepsini geri koyar.
- İki kez çalıştırmak güvenli: shotsort'un `tarih_başlık` biçiminde olan dosyaya
  dokunulmaz.
- İsim çakışmaları asla üzerine yazmaz — ikinci dosya `-1`, `-2` alır.

## Diller

OCR kalitesi, kurulu Tesseract dil paketlerine bağlıdır. Varsayılan `tur+eng`;
shotsort kurulu olmayan dili otomatik atar, böylece hata vermez, İngilizce'ye
döner. Paket yöneticinle daha fazlasını kur (ör. `tesseract-ocr-tur`).

## Geliştirme

```bash
pip install -e ".[dev]"
pytest            # 23 test
ruff check src tests
```

OCR'sız çalışan ilginç çekirdek `naming.py` — başlığın nasıl seçildiğini
iyileştirmek en değerli katkı. Ayrı bir test kümesi gerçek metinli görüntüler
üretip Tesseract'tan geçirir ve çıkan isimleri kontrol eder; bunlar Tesseract
kurulu değilse otomatik atlanır.

## Katkı

Yapay zekâ destekli katkılar sorun değil; yeter ki pull request'te belirt ve
gönderdiğin kodu açıklayabil.

## Lisans

MIT — [LICENSE](LICENSE) dosyasına bak.
