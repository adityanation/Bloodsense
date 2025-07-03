from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

def generate_pdf_report(user_data, health_advice):
    """Generate a PDF report with user data and health advice."""
    # Create a temporary file path
    output_path = os.path.join('temp', f"report_{user_data['name'].replace(' ', '_')}.pdf")
    os.makedirs('temp', exist_ok=True)
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Create custom style for user info
    user_info_style = ParagraphStyle(
        'UserInfo',
        parent=normal_style,
        fontSize=10,
        spaceAfter=12
    )
    
    # Build the PDF content
    story = []
    
    # Add title
    story.append(Paragraph("BloodSense Health Report", title_style))
    story.append(Spacer(1, 30))
    
    # Add user information
    story.append(Paragraph("Patient Information", heading_style))
    story.append(Spacer(1, 12))
    
    user_info = [
        f"Name: {user_data['name']}",
        f"Age: {user_data['age']}",
        f"Gender: {user_data['gender']}",
        f"Height: {user_data['height']}",
        f"Weight: {user_data['weight']}",
        f"Diet: {user_data['diet']}",
        f"Smoking: {user_data['smoke']}",
        f"Alcohol: {user_data['drink']}",
        f"Activity Level: {user_data['activity']}"
    ]
    
    for info in user_info:
        story.append(Paragraph(info, user_info_style))
    
    story.append(Spacer(1, 20))
    
    # Add health advice
    story.append(Paragraph("Health Analysis & Recommendations", heading_style))
    story.append(Spacer(1, 12))
    
    # Split health advice into paragraphs and add them
    paragraphs = health_advice.split('\n\n')
    for para in paragraphs:
        if para.strip():
            story.append(Paragraph(para, normal_style))
            story.append(Spacer(1, 12))
    
    # Add footer
    story.append(Spacer(1, 30))
    footer_text = """
    Disclaimer: This report is generated based on the provided blood test results and personal information.
    It should not be considered as a substitute for professional medical advice. Please consult with your
    healthcare provider before making any changes to your diet, exercise, or medication routine.
    """
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=8,
        textColor=colors.gray
    )))
    
    # Build the PDF
    doc.build(story)
    
    return output_path 