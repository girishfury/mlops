# Remove all emojis and special characters to ensure PDF generation works
import re

# Function to remove emojis and non-ASCII characters
def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)

# Rebuild roadmap with clean text
clean_roadmap = [(clean_text(title), clean_text(level), [clean_text(task) for task in tasks]) for title, level, tasks in roadmap]

# Create PDF again with cleaned text
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Title
pdf.set_font("Arial", 'B', 14)
pdf.cell(200, 10, txt="MLOps Roadmap (DevOps to MLOps - AWS Focused)", ln=True, align='C')
pdf.ln(5)

# Date
pdf.set_font("Arial", size=10)
pdf.cell(200, 10, txt=f"Generated: {datetime.date.today()}", ln=True, align='R')
pdf.ln(10)

# Render each phase in PDF again
for phase_title, level, tasks in clean_roadmap:
    clean_title = f"{phase_title} - {level}"
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=clean_title, ln=True)
    pdf.set_font("Arial", size=11)
    for task in tasks:
        pdf.cell(200, 8, txt=f"- [ ] {task}", ln=True)
    pdf.ln(4)

# Save PDF
pdf_path = "/mnt/data/mlops_roadmap.pdf"
pdf.output(pdf_path)

pdf_path
