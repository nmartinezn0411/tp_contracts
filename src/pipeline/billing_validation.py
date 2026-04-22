'''
Pipeline process to generate 
'''
import pandas as pd
from src.config.settings import settings
from src.pipeline.llm import generate_analysis

def pipeline_process():
    # Read the CSV files
    timesheet_df = pd.read_csv(settings.timesheet)
    billing_df = pd.read_csv(settings.billing)
    contracts_df = pd.read_csv(settings.contracts)

    # MERGE ALL THE DATAFRAMES

    # Merge timesheet with billing
    df = timesheet_df.merge(billing_df, on=["Employee_ID", "Project"], how="outer")

    # Merge with contracts
    df = df.merge(contracts_df, on="Project", how="left")

    # Calculate billing columns
    df["Expected_Billing"] = df["Hours_Worked"] * df["Rate_per_Hour"]
    df["Actual_Billing"] = df["Hours_Billed"] * df["Rate_Charged"]

    # Add flag for rate mismatch
    df["Rate_Mismatch"] = df["Rate_Charged"] != df["Rate_per_Hour"]

    # Add flag for hours mismatch 
    df["Hours_Mismatch"] = df["Hours_Worked"] != df["Hours_Billed"]

    # Add max hours per week mismatched
    df["Exceeds_Max_Hours"] = df["Hours_Worked"] > df["Max_Hours_Per_Week"]

    # Add max billing flag
    df["Overbilling"] = df["Actual_Billing"] > df["Expected_Billing"]

    # FINAL STATUS COLUMN

    df["Status"] = df.apply(
        lambda row: "ERROR" if (
            row["Rate_Mismatch"] or 
            row["Hours_Mismatch"] or 
            row["Exceeds_Max_Hours"] or 
            row["Overbilling"]
        ) else "OK",
        axis=1
    )
    
    # GENERATE AI ANALYSIS
    for idx, row in df.iterrows():
        df.at[idx, "AI_ANALYSIS"] = "EXAMPLE"

    df.to_json(settings.output_file, orient="records", indent=4)
    
    return("Pipeline complete Succesfully")