# Canvas API Academic Data Collector (v1.0)

## Project Structure

The project has been reorganized for better maintainability:

```
canvas_api/
├── config/             # Configuration files
│   ├── config.py       # Main configuration
│   ├── credentials.json
│   └── .env
├── data/               # Data storage
│   ├── grades.csv
│   └── assignments.csv (planned)
├── data_collectors/    # Data collectors
│   ├── grades.py
│   └── assignments.py (planned)
├── docs/               # Documentation
│   ├── readme.md
│   └── readme.pdf
├── emails/             # Email functionality
│   ├── notifier/       # Email sending code
│   └── templates/      # Email templates
├── logs/               # Log files
│   ├── canvas_api.log
│   └── canvas_agent.log
├── notion_processor/   # Notion integration
├── schedulers/         # Scheduling scripts
│   ├── com.bcm.canvas.grades.plist
│   └── setup_scheduler.sh
├── utils/              # Utility modules
├── main.py             # Main entry point
└── requirements.txt    # Dependencies
```

## Running the Application

```bash
# Run manually
python main.py

# Install scheduler
./schedulers/setup_scheduler.sh
```

See full documentation in the docs/ directory.
