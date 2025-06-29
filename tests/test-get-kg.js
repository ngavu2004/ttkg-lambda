import axios from 'axios';

const API_BASE_URL = 'https://rj66xwfu1d.execute-api.us-east-1.amazonaws.com/Prod';
const API_KEY = 'Q5f3OA9qsy4k43wDlZsJm8HOJ63db3vZxbtOlxm5';

// Configure axios with default headers
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
    'X-Api-Key': API_KEY
  }
});

// Test knowledge graph
async function testKnowledgeGraph() {
  try {
    const response = await apiClient.post('/get_knowledge_graph', {
      text: "John Doe works at Microsoft as a software engineer."
    });
    
    console.log('Success:', response.data);
  } catch (error) {
    console.error('Error:', error.response?.data || error.message);
  }
}

testKnowledgeGraph();