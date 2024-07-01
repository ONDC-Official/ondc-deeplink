import qrcode
from PIL import Image
import os
import csv
from qr_code_generator.constants import mapping
from pypdf import PdfWriter, PdfReader, Transformation
from io import BytesIO
from PIL import Image




def bulk_read(data_file, qr_list = []):
    with open(data_file, mode ='r', encoding='utf-8-sig') as file: 
        csvFile = csv.DictReader(file)
        for row in csvFile:
            data = dict(row)
            qr_data={}
            for key, value in data.items():
                if key in mapping.KEY_MAPPING:
                    k = mapping.KEY_MAPPING[key]
                    qr_data[k] = value
            qr_list.append(qr_data)
    print(qr_list)
    return qr_list

#  Generate deep link
def generate_deep_link(deep_link):
    params = mapping.DEFAULT_PARAMS.copy()
    params.update(deep_link)
    try:
        domain = (deep_link.get('context.domain', 'ondc')).lower() # Returns 'default_value as ondc'
        if ':' in domain:
            domain = domain.split(':')[1]
        # print("domain", domain)
    except Exception as e:
        print(f"domain not provided", e)
    BASE_URL = f"{mapping.BASE_URL}{domain}.ondc"
    query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
    # fallback_url = "https://google.com"
    print(f"{BASE_URL}?{query_string}")
    return f"{BASE_URL}?{query_string}"

#  Generate QR code with deep link embedded

def generate_qr_code(deep_link, output):
    """
    Generate a QR code from a given deep link.

    Parameters:
    - deep_link (str): The deep link to encode in the QR code.
    - file_name (str): The name of the file to save the QR code image. Default is "qr_code.png".

    Returns:
    - None
    """
    try:
        # load ONDC logo
        logo_path = os.path.join(os.path.dirname(__file__), "assets/ondc-network-vertical.png")

        # Create QR code with deep link embedded
        qr = qrcode.QRCode(
            # version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=4,
            border=0,
        )
        qr.add_data(deep_link)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        qr_img = img.convert("RGBA")

        # # Load the logo image
        logo = Image.open(logo_path)
        logo = logo.convert("RGBA")

        # taking base width
        basewidth = 80

        # adjust image size
        wpercent = (basewidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        logo = logo.resize((basewidth, hsize), Image.LANCZOS)

        # # Calculate the position to center the logo on the QR code
        logo_position = ((qr_img.size[0] - logo.size[0]) // 2, (qr_img.size[1] - logo.size[1]) // 2)

        # # Paste the logo onto the QR code
        qr_img.paste(logo, logo_position, logo)

        qr_img.save(f"{output}.png")
        print(f"{output}.png")
        qr_template(output)

    except FileNotFoundError:
        print(f"Logo file not found at: {logo_path}")
        raise
    except Exception as e:
        print(f"Exception at: {e}")
        raise

def image_to_pdf(stamp_img) -> PdfReader:
    img = Image.open(stamp_img)
    img = img.convert('RGB')
    img_as_pdf = BytesIO()
    img.save(img_as_pdf, "pdf")
    return PdfReader(img_as_pdf)

def qr_template(qr_img):
    output = PdfWriter()
    template_path = os.path.join(os.path.dirname(__file__), "assets/Poster.pdf")
    input1 = PdfReader(template_path)

    input = input1.pages[0]

    # watermark = open("./assets/qr.png", "rb")
    qr_pdf = image_to_pdf(f"{qr_img}.png")
    output.append(input1)
    output.pages[0].merge_transformed_page(
            qr_pdf.pages[0],
            Transformation().scale(sx=0.52, sy=0.52).translate(tx=283, ty=530),
        )

    output_pdf = f"{qr_img}.pdf"
    outputStream = open(output_pdf, "wb")
    output.write(outputStream)
    outputStream.close()