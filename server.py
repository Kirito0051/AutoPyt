from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List
import pandas as pd
import io
import os
import uuid
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo

app = FastAPI()

# Directory to save processed files
OUTPUT_DIR = "processed"

# Ensure output directory exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    processed_files = []  # List to store paths of processed files

    # Loop through each file
    for file in files:
        original_filename = file.filename
        processed_filename = f"processed_{uuid.uuid4().hex}_{original_filename}"

        # Read the CSV file content
        contents = await file.read()

        try:
            # Attempt to read the CSV file and skip problematic lines
            df = pd.read_csv(io.BytesIO(contents), low_memory=False, on_bad_lines='skip')
        except Exception as e:
            # Return a detailed error message if the file cannot be processed
            return JSONResponse(status_code=400, content={"error": f"Error reading file {original_filename}: {e}"})
        
        # Check the number of rows before filtering
        print(f"Total rows in the original data for {original_filename}: {len(df)}")

        # Filter required columns
        columns_to_extract = [
            "Case ID", "Mother name", "User name", "User Phone", "User Role",
            "Child ID", "Child Name", "Child DOB", "Child Weight Zscore",
            "Last Weight Zscore", "Mother Location", "User Block/Project/Tehsil",
            "User Facility/Center"
        ]
        
        # Check if all the required columns are present
        missing_columns = [col for col in columns_to_extract if col not in df.columns]
        if missing_columns:
            return JSONResponse(status_code=400, content={"error": f"Missing columns in {original_filename}: {missing_columns}"})

        df = df[columns_to_extract]

        # Segregate based on z-score
        zscore_column = 'Last Weight Zscore'
        df_suw = df[df[zscore_column] <= -3]
        df_muw = df[(df[zscore_column] > -3) & (df[zscore_column] <= -2)]
        df_mild = df[(df[zscore_column] > -2) & (df[zscore_column] <= -1)]

        # Save into an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_suw.to_excel(writer, sheet_name="SUW", index=False)
            df_muw.to_excel(writer, sheet_name="MUW", index=False)
            df_mild.to_excel(writer, sheet_name="Mild", index=False)

        output.seek(0)

        # Load workbook for formatting
        wb = load_workbook(filename=output)
        for sheet_name in ["SUW", "MUW", "Mild"]:
            ws = wb[sheet_name]

            table = Table(displayName=f"Table_{sheet_name}", ref=ws.dimensions)
            style = TableStyleInfo(name="TableStyleLight1", showFirstColumn=False,
                                   showLastColumn=False, showRowStripes=True, showColumnStripes=False)
            table.tableStyleInfo = style
            ws.add_table(table)

            for col_idx, col in enumerate(ws.columns, 1):
                max_length = max((len(str(cell.value)) for cell in col if cell.value), default=0)
                adjusted_width = max_length + 2
                ws.column_dimensions[get_column_letter(col_idx)].width = adjusted_width

        # Save the final file to an in-memory byte buffer again
        final_output = io.BytesIO()
        wb.save(final_output)
        final_output.seek(0)

        # Save the file to the 'processed' folder
        output_path = os.path.join(OUTPUT_DIR, processed_filename)
        with open(output_path, "wb") as f:
            f.write(final_output.getbuffer())

        # Add the path to the processed file to the list
        processed_files.append(output_path)

    # Return the list of processed file paths
    return {"processed_files": processed_files}
