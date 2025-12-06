// bibleApi.js
// Connects the React frontend to the FastAPI backend

const API_URL = "http://127.0.0.1:8000/api/query";

export async function askBibleQuestion(payload) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    return data;

  } catch (error) {
    console.error("Error calling backend:", error);
    throw error;
  }
}
