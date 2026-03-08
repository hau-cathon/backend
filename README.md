Backend

Local development quick start:

1. Install dependencies:
	 `pip install -r requirements.txt`
2. Start API:
	 `python run.py`

Seed sample data in MongoDB:

- Idempotent seed for demo records only:
	`python scripts/seed_sample_data.py`
- Full reset of domain collections before seed:
	`python scripts/seed_sample_data.py --clear-all`

The seed script inserts sample:
- issues
- action history
- email history
- email case types
- email templates
- template options
- users and roles
