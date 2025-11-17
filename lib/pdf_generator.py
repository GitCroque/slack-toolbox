#!/usr/bin/env python3
"""
PDF generation utilities for Slack reports
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime


class PDFReport:
    """Generate professional PDF reports"""

    def __init__(self, filename, title="Slack Workspace Report", pagesize=letter):
        self.filename = filename
        self.title = title
        self.doc = SimpleDocTemplate(filename, pagesize=pagesize,
                                     leftMargin=0.75*inch, rightMargin=0.75*inch,
                                     topMargin=1*inch, bottomMargin=0.75*inch)
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#4A5568'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2D3748'),
            spaceAfter=12,
            spaceBefore=12,
            borderColor=colors.HexColor('#667eea'),
            borderWidth=0,
            borderPadding=5
        ))

        # Subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#4A5568'),
            spaceAfter=6
        ))

    def add_title(self, title=None):
        """Add report title"""
        if title is None:
            title = self.title

        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        self.story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        ))
        self.story.append(Spacer(1, 0.3*inch))

    def add_heading(self, text):
        """Add section heading"""
        self.story.append(Paragraph(text, self.styles['CustomHeading']))

    def add_subheading(self, text):
        """Add subsection heading"""
        self.story.append(Paragraph(text, self.styles['CustomSubHeading']))

    def add_paragraph(self, text):
        """Add paragraph of text"""
        self.story.append(Paragraph(text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.1*inch))

    def add_table(self, data, headers=None, col_widths=None):
        """Add a formatted table"""
        if headers:
            table_data = [headers] + data
        else:
            table_data = data

        # Create table
        if col_widths:
            table = Table(table_data, colWidths=col_widths)
        else:
            table = Table(table_data)

        # Style table
        style = TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')])
        ])

        table.setStyle(style)
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))

    def add_key_metrics(self, metrics):
        """Add key metrics in a nice box"""
        data = [[k, str(v)] for k, v in metrics.items()]

        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EDF2F7')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2D3748')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))

    def add_spacer(self, height=0.2):
        """Add vertical space"""
        self.story.append(Spacer(1, height*inch))

    def add_page_break(self):
        """Add page break"""
        self.story.append(PageBreak())

    def build(self):
        """Build and save the PDF"""
        self.doc.build(self.story)


def generate_user_report_pdf(users_data, filename="users_report.pdf"):
    """Generate PDF report for users"""
    pdf = PDFReport(filename, "Slack Users Report")

    # Title
    pdf.add_title()

    # Summary metrics
    pdf.add_heading("Summary")
    metrics = {
        "Total Users": len(users_data),
        "Active Users": len([u for u in users_data if u.get('status') == 'Active']),
        "Admins": len([u for u in users_data if 'Admin' in u.get('role', '')]),
        "Guests": len([u for u in users_data if 'Guest' in u.get('role', '')])
    }
    pdf.add_key_metrics(metrics)

    # User table
    pdf.add_heading("User Details")

    headers = ['Name', 'Email', 'Role', 'Status']
    table_data = []

    for user in users_data[:50]:  # Limit to 50 for PDF
        table_data.append([
            user.get('display_name', '')[:30],
            user.get('email', '')[:35],
            user.get('role', '')[:20],
            user.get('status', '')
        ])

    pdf.add_table(table_data, headers=headers)

    if len(users_data) > 50:
        pdf.add_paragraph(f"<i>Showing first 50 of {len(users_data)} users</i>")

    pdf.build()


def generate_audit_report_pdf(audit_data, filename="audit_report.pdf"):
    """Generate PDF audit report"""
    pdf = PDFReport(filename, "Security Audit Report")

    # Title
    pdf.add_title()

    # Workspace info
    if 'workspace_stats' in audit_data:
        pdf.add_heading("Workspace Overview")
        pdf.add_key_metrics(audit_data['workspace_stats'])

    # Security issues
    if 'security_issues' in audit_data and audit_data['security_issues']:
        pdf.add_heading("Security Issues")

        headers = ['Severity', 'Type', 'User', 'Email']
        table_data = []

        for issue in audit_data['security_issues']:
            table_data.append([
                issue.get('severity', ''),
                issue.get('type', '')[:30],
                issue.get('user', '')[:25],
                issue.get('email', '')[:30]
            ])

        pdf.add_table(table_data, headers=headers)
    else:
        pdf.add_paragraph("<b>✅ No security issues found!</b>")

    # Recommendations
    if 'recommendations' in audit_data and audit_data['recommendations']:
        pdf.add_heading("Recommendations")

        for i, rec in enumerate(audit_data['recommendations'], 1):
            pdf.add_paragraph(f"{i}. {rec}")

    pdf.build()


def generate_activity_report_pdf(activity_data, filename="activity_report.pdf"):
    """Generate PDF activity report"""
    pdf = PDFReport(filename, "Workspace Activity Report")

    # Title
    pdf.add_title()

    # Workspace stats
    if 'workspace_stats' in activity_data:
        pdf.add_heading("Workspace Statistics")
        pdf.add_key_metrics(activity_data['workspace_stats'])

    # Top channels
    if 'top_channels' in activity_data and activity_data['top_channels']:
        pdf.add_heading("Most Active Channels")

        headers = ['Channel', 'Messages', 'Participants', 'Members']
        table_data = []

        for ch in activity_data['top_channels']:
            table_data.append([
                f"#{ch['name']}"[:30],
                str(ch['messages']),
                str(ch['participants']),
                str(ch['members'])
            ])

        pdf.add_table(table_data, headers=headers)

    # File stats
    if 'file_stats' in activity_data:
        pdf.add_heading("File Sharing Statistics")
        pdf.add_key_metrics({
            "Total Files": activity_data['file_stats'].get('total_files', 0),
            "Total Size": activity_data['file_stats'].get('total_size_formatted', 'N/A')
        })

    pdf.build()
