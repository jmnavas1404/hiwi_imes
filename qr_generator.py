# pip install qrcode[pil]
import qrcode

url = "https://github.com/jmnavas1404/hiwi_imes.git"

qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,  # tolera daños/suciedad
    box_size=12,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save("qr_estudiantes.png")