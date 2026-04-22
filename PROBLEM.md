## Scenario: Billing Validation Prototype

You are provided with datasets representing timesheets, contract rates, and billing reports. Your task is to identify discrepancies and flag errors before invoices are sent to the client.

### Data description

- timesheet.csv → Contains employee hours worked per project
- contracts.csv → Contains contractual rates and max allowed hours
- billing.csv → Contains actual billed hours and rate

Use these datasets to identify discrepancies such as overbilling, rate mismatches, and contract violations

### Requirements.

1. Load and process input data (CSV or Excel)
2. Compare expected vs actual billing values
3. Identify discrepancies such as rate mismatches, missing hours, and overbilling
4. Generate a clean output dataset with flags (OK / ERROR)
5. Automate the workflow (Make.com or Python)
6. Use AI (OpenAI / Claude) to explain discrepancies and suggest corrective actions
7. Provide results via a simple interface (optional but recommended)
8. Deliver the solution via a structured GitHub repository

### Github Deliverables

1. Organized repository structure (data, scripts, prompts, workflows)
2. README file with clear explanation and instructions
3. Version control with meaningful commits


### Bonus Challenge

Design your solution so it can support multiple clients with different contract rules without requiring code changes