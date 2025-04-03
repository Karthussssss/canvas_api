# Canvas API Email Report System

This directory contains tools for generating and sending HTML email reports with Canvas grades data.

## Overview

The email report system provides:
- Beautiful HTML reports with student performance data
- Email notifications for success and failure scenarios
- Detailed analytics on student grades across courses
- Privacy statements in English and Chinese
- Beecoming Inc. branding throughout

## Setup

### Email Credentials

Email credentials are configured in the `config/.env` file with these variables:

```
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

**Note for Gmail users**: You'll need to use an App Password rather than your regular password.
1. Enable 2-Step Verification on your Google Account
2. Go to Security > App passwords
3. Generate a new app password for "Mail"
4. Use this password in your `.env` file

## Using the Report System

### Integration with main workflow

The report system is automatically integrated with the main data collection workflow. When the main script runs, it will:
1. Collect grades data from Canvas
2. Process the data for Notion
3. Generate an HTML report with analytics
4. Send an email with the report to the configured recipient

This requires no manual intervention once set up properly.

### Generating a Test Report

To generate a test HTML report without sending an email:

```bash
python emails/test_report.py
```

This will create an HTML report at `emails/generated/test_report.html` and open it in your browser.

## Report Components

The email report includes:
- Beecoming Inc. logo at the top and bottom
- Overall performance statistics
- Course enrollment and average scores
- Students with D and F grades (requiring immediate attention)
- Students at risk of dropping from A to B (scores between 90-92.5%)
- Privacy statement in English and Chinese
- Author credit

## Troubleshooting

If you encounter issues with email sending:

1. **Authentication errors**: Make sure you're using the correct username and password. For Gmail, use an App Password.
2. **Connection errors**: Check that your SMTP server and port are correct.
3. **Timeout errors**: Some networks block outgoing SMTP connections. Try from a different network.
4. **HTML rendering issues**: Check the HTML file generated at `emails/generated/grades_report.html`.

## File Structure

- `templates/`: Email HTML templates
- `generated/`: Generated HTML reports
- `notifier/`: Classes for sending email notifications
- `report_generator.py`: Main report generation logic
- `test_report.py`: Tool for generating test reports

## Maintenance

The email report system is designed to be maintainable and extensible. Key components:

1. **Template System**: The HTML template in `templates/report_template.html` can be modified to change the layout and style of the reports.
2. **Report Generator**: The `report_generator.py` file contains the logic for transforming data into HTML reports.
3. **Email Notifiers**: The `notifier/` directory contains classes for sending emails in various formats. 