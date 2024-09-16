'use server';

import db from "@/lib/db";

// Insert and sync Google Sheets data with MySQL
export const syncGoogleSheetDataToMySQL = async (sheetData: any[][]) => {
  try {
    // Fetch existing data from MySQL
    const [dbRows] = await db.query(
      'SELECT col1, col2, col3 FROM GoogleSheetData'
    );
    
    const dbData = dbRows.map((row: any) => [row.col1, row.col2, row.col3]);

    // Find the rows that exist in the database but not in the Google Sheet (deletions)
    const rowsToDelete = dbData.filter(
      (dbRow:any) => !sheetData.some((sheetRow) => 
        JSON.stringify(sheetRow) === JSON.stringify(dbRow)
      )
    );

    // Delete rows that are no longer in the Google Sheet
    for (const row of rowsToDelete) {
      const [col1, col2, col3] = row;
      await db.query(
        'DELETE FROM GoogleSheetData WHERE col1 = ? AND col2 = ? AND col3 = ?',
        [col1, col2, col3]
      );
    }

    // Insert or update rows from Google Sheet into MySQL
    for (const row of sheetData) {
      const [col1, col2, col3] = row;
      
      // Upsert logic: Insert new data or update existing data
      await db.query(
        `INSERT INTO GoogleSheetData (col1, col2, col3)
        VALUES (?, ?, ?)
        ON DUPLICATE KEY UPDATE col2 = VALUES(col2), col3 = VALUES(col3)`,
        [col1, col2, col3]
      );
    }

    return { success: true, message: 'Google Sheets data synced with MySQL successfully!' };
  } catch (error) {
    console.error('Error syncing Google Sheets data to MySQL:', error);
    return { success: false, message: 'Error syncing Google Sheets data to MySQL.' };
  }
};
