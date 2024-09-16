import { google } from 'googleapis';


const getGoogleSheetData = async () => {
  const auth = new google.auth.GoogleAuth({
    credentials:{
        client_email:process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key:process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g,"\n")
    },
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });

  const sheets = google.sheets(
    { 
        version: 'v4',
        //  auth:await auth.getClient()
        auth
  });

  const range = 'Sheet1!A:Z';
    try {
        
         const response = await sheets.spreadsheets.values.get({
    spreadsheetId:process.env.GOOGLE_SHEET_ID,
    range,
  });
  console.log(response.data.values);
  

  return response.data.values;
    } catch (error) {
        console.error("Error from getGoogleSheetData :",error)
    }
};

const updateGoogleSheet = async (data: string[][]|any[][]) => {
  const auth = new google.auth.GoogleAuth({
    credentials:{
        client_email:process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
        private_key:process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g,"\n")
    },
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });

  const sheets = google.sheets({ version: 'v4', auth });
  const range = 'Sheet1!A:Z';

  await sheets.spreadsheets.values.update({
    spreadsheetId:process.env.GOOGLE_SHEET_ID,
    range,
    valueInputOption: 'RAW',
    requestBody: {
      values:data,
    },
  });
  console.log("success from updateGoogleSheet/sheet.ts");
  
};

export { getGoogleSheetData, updateGoogleSheet };

