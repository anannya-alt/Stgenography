from flask import Flask, render_template, request, send_file
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# =========================
# ENCODE FUNCTION
# =========================
def encode_message(image_path, message, output_path):
    img = Image.open(image_path).convert("RGB")
    encoded = img.copy()
    width, height = img.size

    message += "###END###"   # End marker
    binary_message = ''.join(format(ord(char), '08b') for char in message)

    data_index = 0
    total_bits = len(binary_message)

    for row in range(height):
        for col in range(width):
            if data_index < total_bits:
                r, g, b = img.getpixel((col, row))

                # Modify least significant bit
                r = (r & ~1) | int(binary_message[data_index])
                data_index += 1

                if data_index < total_bits:
                    g = (g & ~1) | int(binary_message[data_index])
                    data_index += 1

                if data_index < total_bits:
                    b = (b & ~1) | int(binary_message[data_index])
                    data_index += 1

                encoded.putpixel((col, row), (r, g, b))
            else:
                encoded.save(output_path)
                return

    encoded.save(output_path)


# =========================
# DECODE FUNCTION
# =========================
def decode_message(image_path):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size

    binary_data = ""
    for row in range(height):
        for col in range(width):
            r, g, b = img.getpixel((col, row))
            binary_data += str(r & 1)
            binary_data += str(g & 1)
            binary_data += str(b & 1)

    # Convert binary to characters
    all_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    decoded_message = ""

    for byte in all_bytes:
        decoded_message += chr(int(byte, 2))
        if decoded_message.endswith("###END###"):
            return decoded_message.replace("###END###", "")

    return "No hidden message found."


# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/encode", methods=["POST"])
def encode():
    image = request.files["image"]
    message = request.form["message"]

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)

    output_path = os.path.join(app.config["UPLOAD_FOLDER"], "encoded_" + image.filename)

    encode_message(image_path, message, output_path)

    return send_file(output_path, as_attachment=True)


@app.route("/decode", methods=["POST"])
def decode():
    image = request.files["image"]

    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
    image.save(image_path)

    hidden_message = decode_message(image_path)

    return f"<h2>Hidden Message:</h2><p>{hidden_message}</p>"


if __name__ == "__main__":
    app.run(debug=True)