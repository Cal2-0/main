from flask import Flask, render_template, request
import PyPDF2
import os

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))

@app.route("/", methods=["GET", "POST"])
def index():
    output = ""
    if request.method == "POST":
            merger = PyPDF2.PdfFileMerger()
            for file in os.listdir(os.curdir):
                if file.endswith(".pdf"):
                    merger.append(file)
            merger.write("combined.pdf")
    return render_template("index.html", output=output)

if __name__ == "__main__":
    app.run(debug=True)
