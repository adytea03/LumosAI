from flask import Flask, render_template, request
from utils import extract_text_from_upload, generate_interview_pack

app = Flask(__name__)
app.secret_key = "interview-ai-secret-key"


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        jd_text = (request.form.get("job_description_text") or "").strip()
        resume_text = (request.form.get("resume_text") or "").strip()
        company_text = (request.form.get("company_description_text") or "").strip()

        jd_removed = request.form.get("remove_job_description_file") == "1"
        resume_removed = request.form.get("remove_resume_file") == "1"
        company_removed = request.form.get("remove_company_file") == "1"

        jd_file = request.files.get("job_description_file")
        resume_file = request.files.get("resume_file")
        company_file = request.files.get("company_file")

        jd_from_file = ""
        resume_from_file = ""
        company_from_file = ""

        if not jd_removed:
            jd_from_file = extract_text_from_upload(jd_file)

        if not resume_removed:
            resume_from_file = extract_text_from_upload(resume_file)

        if not company_removed:
            company_from_file = extract_text_from_upload(company_file)

        final_jd = "\n".join([part for part in [jd_text, jd_from_file] if part]).strip()
        final_resume = "\n".join([part for part in [resume_text, resume_from_file] if part]).strip()
        final_company = "\n".join([part for part in [company_text, company_from_file] if part]).strip()

        if not final_jd or not final_resume:
            error = "Job Description and Resume are mandatory. You can type them, upload files, or use both."
        else:
            try:
                question_count = int(request.form.get("question_count", 9))
            except ValueError:
                question_count = 9

            question_count = max(5, min(question_count, 15))

            result = generate_interview_pack(
                jd_text=final_jd,
                resume_text=final_resume,
                company_text=final_company,
                question_count=question_count
            )

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)