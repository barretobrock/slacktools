import json
import os

import pandas as pd
import pygsheets

from slacktools.secretstore import SecretStore


class GSheetAgent:
    """A class to help with reading in Google Sheets"""
    def __init__(self, sec_store: SecretStore, sheet_key: str):
        creds = sec_store.get_key('gsheet-reader')
        os.environ['GDRIVE_API_CREDENTIALS'] = json.dumps(creds)
        self.gc = pygsheets.authorize(service_account_env_var='GDRIVE_API_CREDENTIALS')
        self.sheets = self.gc.open_by_key(sheet_key).worksheets()

    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Retrieves a sheet as a pandas dataframe"""
        for sheet in self.sheets:
            if sheet.title == sheet_name:
                return sheet.get_as_df()
        raise ValueError(f'The sheet name "{sheet_name}" was not found '
                         f'in the list of available sheets: ({",".join([x.title for x in self.sheets])})')

    def write_df_to_sheet(self, sheet_key: str, sheet_name: str, df: pd.DataFrame):
        """Write df to sheet"""
        wb = self.gc.open_by_key(sheet_key)
        sheet = wb.worksheet_by_title(sheet_name)
        sheet.clear()
        sheet.set_dataframe(df, (1, 1))
