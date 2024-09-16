
import { syncGoogleSheetDataToMySQL } from "@/actions/fetchdata";
import { getGoogleSheetData } from "@/lib/sheet";


export default async function HomePage() {
  // Fetch data from Google Sheets
  const data = await getGoogleSheetData();
  console.log("Fetched data from Google Sheets:", data);

  // Sync data with MySQL (handle insert, update, and delete)
  const result = await syncGoogleSheetDataToMySQL(data!);
  console.log(result);



  return (
    <div className="bg-gray-100 min-h-screen flex items-center justify-center text-black p-5">
      <div className="container mx-auto">
        <h1 className="text-3xl font-bold mb-5 text-center">Google Sheets Data</h1>
        <table className="table-auto w-full max-w-3xl mx-auto text-center border-collapse border border-gray-300">
          <thead>
            <tr className="bg-gray-200">
              <th className="border border-gray-300 px-4 py-2">Col1</th>
              <th className="border border-gray-300 px-4 py-2">Col2</th>
              <th className="border border-gray-300 px-4 py-2">Col3</th>
            </tr>
          </thead>
          <tbody>
            {data?.map((row, index) => (
              <tr key={index} className="bg-white hover:bg-gray-100">
                <td className="border border-gray-300 px-4 py-2">{row[0]}</td>
                <td className="border border-gray-300 px-4 py-2">{row[1]}</td>
                <td className="border border-gray-300 px-4 py-2">{row[2]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
